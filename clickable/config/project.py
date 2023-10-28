import os
import platform
import re
import multiprocessing
from pathlib import PurePath
from collections import OrderedDict

import yaml

from clickable.config.base import BaseConfig
from clickable.system.queries.nvidia_drivers_in_use import NvidiaDriversInUse
from clickable.version import __version__, get_major_version, is_newer_than_running, \
    split_version_numbers
from clickable.exceptions import ClickableException

from .libconfig import LibConfig, LibInitConfig
from .file_helpers import InstallFiles, ProjectFiles
from .constants import Constants
from .global_config import GlobalConfig
from .environment import EnvironmentConfig

from ..utils import (
    merge_make_jobs_into_args,
    get_make_jobs_from_args,
    flexible_string_to_list,
    env,
    validate_config_format,
    make_absolute,
    make_env_var_conform,
    is_path_sane,
    let_user_confirm,
    load_config_schema,
)
from ..logger import logger


class ProjectConfig(BaseConfig):
    config = {}

    ENV_MAP = {
        'CLICKABLE_ARCH': 'restrict_arch_env',
        'CLICKABLE_FRAMEWORK': 'framework',
        'CLICKABLE_QT_VERSION': 'qt_version',
        'CLICKABLE_BUILDER': 'builder',
        'CLICKABLE_BUILD_DIR': 'build_dir',
        'CLICKABLE_DEFAULT': 'default',
        'CLICKABLE_MAKE_JOBS': 'make_jobs',
        'GOPATH': 'gopath',
        'CLICKABLE_DOCKER_IMAGE': 'docker_image',
        'CLICKABLE_BUILD_ARGS': 'build_args',
        'CLICKABLE_MAKE_ARGS': 'make_args',
        'CLICKABLE_ALWAYS_CLEAN': 'always_clean',
        'CLICKABLE_TEST': 'test',
    }

    static_placeholders = OrderedDict({
        "SDK_FRAMEWORK": "framework",
        "QT_VERSION": "qt_version",
        "ARCH": "arch",
        "ARCH_TRIPLET": "arch_triplet",
        "ARCH_RUST": "arch_rust",
        "NUM_PROCS": "make_jobs",
        "ROOT": "root_dir",
        "BUILD_DIR": "build_dir",
        "SRC_DIR": "src_dir",
        "INSTALL_DIR": "install_dir",
        "CLICK_LD_LIBRARY_PATH": "app_lib_dir",
        "CLICK_PATH": "app_bin_dir",
        "CLICK_QML2_IMPORT_PATH": "app_qml_dir",
    })
    libs_placeholders = ["install_dir", "build_dir", "src_dir"]
    accepts_placeholders = ["root_dir", "build_dir", "src_dir", "install_dir",
                            "app_lib_dir", "app_bin_dir", "app_qml_dir",
                            "gopath", "cargo_home", "scripts", "build",
                            "build_args", "make_args", "postmake", "postbuild",
                            "prebuild",
                            "install_lib", "install_qml", "install_bin", "install_root_data",
                            "install_data", "env_vars", "build_home",
                            "dependencies_host", "dependencies_target", "dependencies_ppa",
                            "build"]

    # Dicts where keys accept placeholders
    accepts_placeholders_keys = ["install_data", "env_vars"]

    # Paths to be checked for sanity, iterates and recurses lists and dicts
    path_keys = ['install_qml', 'install_bin', 'install_lib']
    # Like `path_keys`, but made absolute
    absolute_path_keys = ['root_dir', 'build_dir', 'src_dir', 'install_dir',
                          'cargo_home', 'gopath', 'app_lib_dir', 'app_bin_dir',
                          'app_qml_dir', 'build_home',
                          'install_root_data']
    # Same as for path_keys, except that for dicts the keys are made
    # absolute, not the values
    path_dict_keys = ['install_data']

    # If specified as a string split at spaces
    flexible_split_list = ['dependencies_host', 'dependencies_target',
                           'dependencies_ppa',
                           'install_lib', 'install_bin', 'install_qml', 'install_root_data',
                           'build_args', 'make_args', 'default', 'ignore']
    # If specified as a string convert it to a list of size 1
    flexible_list = ['prebuild', 'build', 'postmake', 'postbuild']
    removed_keywords = ['chroot', 'sdk', 'package', 'app', 'premake', 'ssh',
                        'dependencies', 'specificDependencies', 'dir', 'lxd',
                        'arch', 'template', 'dependencies_build', 'dirty']

    first_docker_info = True
    container_mode = False
    use_nvidia = False
    avoid_nvidia = False
    verbose = False
    interactive = True
    build_arch = None
    container_list = []
    install_files = None
    lib_configs = []
    global_config = None
    skip_image_setup = False
    arch_inferred = False

    def __init__(self, custom_path=None, cwd=None):
        super().__init__()

        self.is_custom_docker_image = False
        self.project_files = None
        self.placeholders = {}
        self.commands = []
        self.configured = False
        self.cwd = cwd if cwd else os.getcwd()

        self.set_default_config()
        self.load(custom_path)

    def set_default_config(self):
        self.config = {
            'clickable_minimum_required': None,
            'arch': None,
            'restrict_arch_env': None,
            'restrict_arch': None,
            'arch_triplet': None,
            'arch_rust': None,
            'builder': None,
            'postmake': None,
            'prebuild': None,
            'build': None,
            'postbuild': None,
            'launch': None,
            'build_dir': '${ROOT}/build/${ARCH_TRIPLET}/app',
            'build_home': '${BUILD_DIR}/.clickable/home',
            'src_dir': '${ROOT}',
            'root_dir': self.cwd,
            'kill': None,
            'scripts': {},
            'default': [],
            'dependencies_host': [],
            'dependencies_target': [],
            'dependencies_ppa': [],
            'install_lib': [],
            'install_bin': [],
            'install_qml': [],
            'install_root_data': [],
            'install_data': {},
            'app_lib_dir': '${INSTALL_DIR}/lib/${ARCH_TRIPLET}',
            'app_bin_dir': '${INSTALL_DIR}/lib/${ARCH_TRIPLET}/bin',
            'app_qml_dir': '${INSTALL_DIR}/lib/${ARCH_TRIPLET}',
            'ignore': [],
            'make_jobs': None,
            'gopath': os.path.join(Constants.clickable_dir, 'go'),
            'cargo_home': os.path.join(Constants.clickable_dir, 'cargo'),
            'docker_image': None,
            'build_args': [],
            'env_vars': {},
            'env_env_vars': {},
            'make_args': [],
            'libraries': {},
            'test': None,
            'install_dir': '${BUILD_DIR}/install',
            'image_setup': {},
            'qt_version': Constants.default_qt,
            'rust_channel': None,
            'framework': None,
            'always_clean': False,
            'skip_review': False,
            'ignore_review_warnings': None,
            'ignore_review_errors': None,
        }

    def load(self, config_path):
        config_dict = self.load_project_config(config_path)
        self.config.update(config_dict)

        self.harmonize_config()

    def configure(self, global_config: GlobalConfig, commands, args=None, device_arch=None,
                  cwd=None, always_clean=False):
        self.global_config = global_config

        self.placeholders.update(ProjectConfig.static_placeholders)

        if not Constants.host_arch:
            raise ClickableException(
                f"No support for host architecture {platform.machine()}"
            )
        self.cwd = cwd if cwd else os.getcwd()
        self.project_files = ProjectFiles(self.cwd)

        self.parse_configs(args, commands, always_clean)
        self.check_paths()
        self.set_builder_interactive()
        self.set_conditional_defaults(device_arch)
        self.setup()
        self.check_config_errors()

        self.configured = True

    def parse_configs(self, args, commands, always_clean):
        env_config = self.load_env_config(self.global_config.environment)
        self.config.update(env_config)
        self.config['env_vars'].update(self.config['env_env_vars'])

        if args:
            arg_config = self.load_arg_config(args)
            self.config.update(arg_config)

        self.merge_cli_config()

        self.commands = commands
        if always_clean:
            self.config['always_clean'] = True

    def setup(self):
        self.ignore.extend([
            '.git', '.bzr', '.clickable', '.gitlab-ci.yml', 'build', '.gitignore', '.bzrignore'
        ])

        self.setup_image()
        self.setup_libs()
        self.handle_path_keys_and_placeholders()

        self.setup_helpers()

        for key, value in self.config.items():
            logger.debug('App config value %s: %s', key, value)

    def set_conditional_defaults(self, device_arch):
        if self.config["docker_image"]:
            self.is_custom_docker_image = True
        else:
            self.is_custom_docker_image = False

        if self.config['arch'] == 'detect':
            if device_arch:
                self.config['arch'] = device_arch
                logger.debug(
                    'Architecture set to "%s" from device detection', self.config['arch']
                )
            else:
                # This should be caught in the device class
                raise ClickableException(
                    'Architecture is set to "detect", but no device detected. '
                    'This seems to be a bug in Clickable.'
                )

        if not self.config["arch"]:
            self.arch_inferred = True

            if self.is_arch_agnostic():
                self.config["arch"] = "all"
                logger.debug(
                    'Architecture set to "all" because builder "%s" is architecture '
                    'agnostic', self.config['builder']
                )
            elif self.is_desktop_mode():
                self.config["arch"] = Constants.host_arch
                logger.debug(
                    'Architecture set to "%s" because of desktop mode.', self.config["arch"]
                )
            elif self.config["restrict_arch"]:
                self.config["arch"] = self.config["restrict_arch"]
            elif self.config["restrict_arch_env"]:
                self.config["arch"] = self.config["restrict_arch_env"]
                logger.debug(
                    'Architecture set to "%s" due to environment restriction',
                    self.config["arch"]
                )
            elif self.container_mode:
                self.config['arch'] = Constants.host_arch
                logger.debug(
                    'Architecture set to "%s" due to container mode', self.config['arch']
                )
            elif device_arch:
                self.config['arch'] = device_arch
                logger.debug(
                    'Architecture set to "%s" from device', self.config['arch']
                )
            elif self.global_config.build.default_arch and \
                    self.global_config.build.default_arch != "detect":
                self.config['arch'] = self.global_config.build.default_arch
                logger.info(
                    'Architecture set to "%s" from Clickable config', self.config['arch']
                )
            else:
                self.config['arch'] = Constants.host_arch
                logger.info(
                    'Architecture set to host arch "%s"', self.config['arch']
                )

        if self.config['arch'] == 'all':
            self.config['app_lib_dir'] = '${INSTALL_DIR}/lib'
            self.config['app_bin_dir'] = '${INSTALL_DIR}'
            self.config['app_qml_dir'] = '${INSTALL_DIR}/qml'

        if self.config["arch"] == "host":
            self.config["arch"] = Constants.host_arch

        if self.config['arch'] not in Constants.arch_triplet_mapping:
            raise ClickableException(
                f'There is currently no support for architecture  "{self.config["arch"]}"'
            )
        self.config['arch_triplet'] = Constants.arch_triplet_mapping[self.config['arch']]

        if Constants.host_arch not in Constants.container_mapping:
            raise ClickableException(
                'Clickable currently does not have docker images for your host '
                f'architecture "{Constants.host_arch}"'
            )

        if not self.config['kill']:
            if self.config['builder'] in [Constants.PURE_QML_CMAKE,
                                          Constants.PURE_QML_QMAKE, Constants.PURE]:
                self.config['kill'] = 'qmlscene'
            else:
                try:
                    desktop = self.project_files.find_any_desktop(self.cwd)
                except ClickableException:
                    desktop = None
                except Exception as e:  # pylint: disable=broad-except
                    logger.debug('Unable to load or parse desktop file', exc_info=e)
                    desktop = None

                if desktop and 'Exec' in desktop:
                    self.config['kill'] = desktop['Exec'] \
                        .replace('%u', '').replace('%U', '').strip()

        self.config['make_args'] = flexible_string_to_list(self.config['make_args'], split=True)

        make_jobs_args = get_make_jobs_from_args(self.config['make_args'])
        if make_jobs_args:
            if self.config['make_jobs']:
                raise ClickableException(
                    'Conflict: Number of make jobs has been specified by both, '
                    '"make_args" and "make_jobs"!'
                )

            logger.warning(
                'Number of make jobs has been set via "make_args". better use '
                '"make_jobs" instead.'
            )
            self.config['make_jobs'] = make_jobs_args
        else:
            if not self.config['make_jobs']:
                self.config['make_jobs'] = multiprocessing.cpu_count()

            self.config['make_args'] = merge_make_jobs_into_args(
                self.config['make_args'], self.config['make_jobs'])

        self.config['make_jobs'] = str(self.config['make_jobs'])

        if not self.config['framework']:
            qt = self.config['qt_version']
            framework = Constants.default_qt_framework_mapping.get(qt, None)

            if not framework:
                raise ClickableException(f'Qt version "{qt}" is not known to Clickable')

            self.config['framework'] = framework

        self.set_build_arch()
        self.config['arch_rust'] = Constants.rust_arch_target_mapping[self.build_arch]

    def get_image_framework(self):
        if self.config['framework'] in Constants.framework_image_mapping:
            return Constants.framework_image_mapping[self.config['framework']]

        return Constants.framework_image_fallback[self.get_framework_base()]

    def get_framework_base(self):
        for base in Constants.framework_base:
            if self.config['framework'].find(base) != -1:
                return base

        return Constants.framework_base_default

    def setup_image(self):
        if self.needs_clickable_image():
            self.check_nvidia_mode()

            container_spec = self.build_arch

            if self.use_nvidia:
                container_spec += "-nvidia"

            if self.is_ide_command():
                container_spec += "-ide"

            image_framework = self.get_image_framework()
            container_mapping_host = Constants.container_mapping[Constants.host_arch]
            container = container_mapping_host.get((image_framework, container_spec), None)

            if not container:
                raise ClickableException(
                    f'There is currently no docker image for {image_framework}-{container_spec}'
                )

            self.config['docker_image'] = container
            self.container_list = list(container_mapping_host.values())

    def setup_helpers(self):
        self.install_files = InstallFiles(
            self.config['install_dir'],
            self.config['builder'],
            self.config['arch'])

    def is_arch_agnostic(self):
        return self.config["builder"] in Constants.arch_agnostic_builders

    def __getattr__(self, name):
        return self.config[name]

    def __setattr__(self, name, value):
        if name in self.config:
            self.config[name] = value
        else:
            super().__setattr__(name, value)

    def find_project_config(self, config_path):
        directory = self.cwd

        while True:
            for option in Constants.project_config_path_options:
                candidate = os.path.join(directory, option)

                if os.path.exists(candidate):
                    config_path = candidate
                    self.config['root_dir'] = directory
                    os.chdir(directory)
                    self.cwd = directory
                    return config_path

            parent = os.path.dirname(directory)
            if parent == directory:
                break
            directory = parent

        return None

    def load_project_config(self, config_path):
        config_dict = {}
        use_default_config = not config_path

        if use_default_config:
            config_path = self.find_project_config(config_path)

        if config_path and os.path.isfile(config_path):
            logger.debug("Loading config file %s", config_path)

            with open(config_path, 'r', encoding='UTF-8') as f:
                file_contents = f.readlines()
                if os.path.splitext(config_path)[1] == '.json':
                    # Handle tabs instead of spaces in json files
                    file_contents = [re.sub('^\t+', '  ', line) for line in file_contents]

                config_dict = {}
                try:
                    config_dict = yaml.safe_load("\n".join(file_contents))

                except ValueError as err:
                    raise ClickableException(
                        f'Project config {config_path} is not a valid yaml file') from err

                for key in self.removed_keywords:
                    if key in config_dict:
                        raise ClickableException(
                            f'"{key}" is no longer a valid configuration option'
                        )

                schema = load_config_schema('project')
                absolute_path = make_absolute(config_path)
                relative_path = PurePath(absolute_path).relative_to(self.config['root_dir'])
                validate_config_format(config_dict, schema, 'project', relative_path)
        elif not use_default_config:
            raise ClickableException(
                f'Specified config file "{config_path}" does not exist.'
            )

        return config_dict

    def merge_cli_config(self):
        if self.global_config.cli.scripts:
            self.config['scripts'].update(self.global_config.cli.scripts)

    def load_env_config(self, config: EnvironmentConfig):
        if self.get_env_var('CLICKABLE_CONTAINER_MODE') or config.container_mode:
            self.container_mode = True

        if self.get_env_var('CLICKABLE_NVIDIA') or config.nvidia == 'on':
            self.use_nvidia = True

        if self.get_env_var('CLICKABLE_NO_NVIDIA') or config.nvidia == 'off':
            self.avoid_nvidia = True

        if self.get_env_var('CLICKABLE_NON_INTERACTIVE') or config.non_interactive:
            self.interactive = False

        if config.restrict_arch:
            self.config["restrict_arch_env"] = config.restrict_arch

        config = {}
        for var, name in self.ENV_MAP.items():
            if self.get_env_var(var):
                config[name] = self.get_env_var(var)

        config["env_env_vars"] = self.get_custom_env_vars(prefix="CLICKABLE_ENV_")

        return config

    def get_custom_env_vars(self, prefix):
        start = len(prefix)
        return {k[start:]: v for k, v in os.environ.items() if k.startswith(prefix)}

    def get_env_var(self, key):
        return env(key)

    def load_arg_config(self, args):
        if args.container_mode:
            self.container_mode = args.container_mode

        if args.nvidia:
            self.use_nvidia = True

        if args.no_nvidia:
            self.avoid_nvidia = True

        if args.verbose:
            self.verbose = True

        if args.non_interactive:
            self.interactive = False

        config = {}
        if args.arch:
            config['arch'] = args.arch

        if args.docker_image:
            config['docker_image'] = args.docker_image

        if args.skip_image_setup:
            self.skip_image_setup = True

        return config

    def prepare_docker_env_vars(self):
        docker_env_vars = []
        env_dict = self.get_env_vars()

        env_dict["HOME"] = self.config["build_home"]

        for key, val in env_dict.items():
            docker_env_vars.append(f'-e {key}="{val}"')

        return " ".join(docker_env_vars)

    def set_env_vars(self):
        os.environ.update(self.get_env_vars())

    def get_env_vars(self):
        env_vars = {}

        if self.config['gopath']:
            env_vars['GOPATH'] = self.config['gopath']

        if self.lib_configs:
            install_dirs = [lib.install_dir for lib in self.lib_configs]
            env_vars['CMAKE_PREFIX_PATH'] = ':'.join(install_dirs)

        for key, conf in self.placeholders.items():
            env_vars[key] = self.config[conf]

        env_vars.update(self.config['env_vars'])

        return env_vars

    def substitute(self, sub, rep, key, change_keys=False):
        if self.config[key]:
            if isinstance(self.config[key], dict):
                items = self.config[key].items()
                if change_keys:
                    self.config[key] = {
                        k.replace(sub, rep): val for (k, val) in items
                    }
                else:
                    self.config[key] = {
                        k: val.replace(sub, rep) for (k, val) in items
                    }
            elif isinstance(self.config[key], list):
                self.config[key] = [val.replace(sub, rep) for val in self.config[key]]
            else:
                self.config[key] = self.config[key].replace(sub, rep)

    def handle_accepting_key(self, key, change_keys=False):
        if not self.config[key]:
            return

        for sub, placeholder in self.placeholders.items():
            rep = self.config[placeholder]
            if rep is None:
                logger.warning("Placeholder '%s' used in '%s' is not set. Skipping...",
                               sub, key)
            else:
                self.substitute("${" + sub + "}", rep, key, change_keys)

    def handle_path_keys_and_placeholders(self):
        # Merge lists preserving order within 'accepts_placeholders'
        accepting = self.accepts_placeholders
        accepting += list(set(accepting) - set(self.accepts_placeholders_keys))

        # Make paths absolute that don't accept placeholders.
        # They may be used as placeholders themselves.
        for key in set(self.absolute_path_keys) - set(accepting):
            self.config[key] = make_absolute(self.config[key], change_keys=False)
        for key in set(self.path_dict_keys) - set(accepting):
            self.config[key] = make_absolute(self.config[key], change_keys=True)

        # One by one inject placeholders and then make paths absolute
        for key in accepting:
            if key in self.accepts_placeholders:
                self.handle_accepting_key(key, change_keys=False)
            if key in self.accepts_placeholders_keys:
                self.handle_accepting_key(key, change_keys=True)

            if key in self.absolute_path_keys:
                self.config[key] = make_absolute(self.config[key], change_keys=False)
            if key in self.path_dict_keys:
                self.config[key] = make_absolute(self.config[key], change_keys=True)

    def set_build_arch(self):
        if self.config['arch'] in ['all', 'host']:
            self.build_arch = Constants.host_arch
        else:
            self.build_arch = self.config['arch']

    def check_nvidia_mode(self):
        if self.is_desktop_mode():
            if self.avoid_nvidia:
                logger.debug('Skipping nvidia driver detection.')
            elif self.use_nvidia:
                logger.debug('Turning on nvidia mode.')
            else:
                if NvidiaDriversInUse().is_met():
                    logger.debug('Nvidia driver detected, turning on nvidia mode.')
                    self.use_nvidia = True
        else:
            self.use_nvidia = False

    def setup_libs(self):
        self.lib_configs = []
        placeholders = {}
        injected_config = {}

        for name, config in self.config['libraries'].items():
            config.update(injected_config)

            lib_init = LibInitConfig()
            lib_init.name = name
            lib_init.config_dict = config
            lib_init.arch = self.config['arch']
            lib_init.arch_inferred = self.arch_inferred
            lib_init.root_dir = self.config['root_dir']
            lib_init.qt_version = self.config['qt_version']
            lib_init.verbose = self.verbose
            lib_init.libs_placeholders = placeholders
            lib_init.lib_configs = self.lib_configs
            lib_init.container_mode = self.container_mode
            lib_init.docker_image = self.docker_image
            lib_init.build_arch = self.build_arch
            lib_init.skip_image_setup = self.skip_image_setup

            lib = LibConfig(lib_init)
            self.lib_configs.append(lib)

            for lp in self.libs_placeholders:
                key = f'{lib.name}_LIB_{lp}'
                placeholder = make_env_var_conform(key)
                placeholders[placeholder] = key
                injected_config[key] = lib.config[lp]

        self.placeholders.update(placeholders)
        self.config.update(injected_config)

    def harmonize_config(self):
        for key in self.flexible_split_list:
            self.config[key] = flexible_string_to_list(self.config[key], split=True)

        for key in self.flexible_list:
            self.config[key] = flexible_string_to_list(self.config[key], split=False)

    def is_desktop_mode(self):
        return bool(set(['desktop', 'test-libs', 'test', 'ide']).intersection(self.commands))

    def is_ide_command(self):
        return "ide" in self.commands

    def is_build_cmd(self):
        return self.is_desktop_mode() or 'build' in self.commands

    def is_project_independent_cmd(self):
        return bool(set(['no_lock', 'writable_image', 'screenshots', 'create', 'setup',
                    'shell', 'devices', 'update-images', 'clean-images']
                        ).intersection(self.commands))

    def is_device_cmd(self):
        return bool(set(['install', 'launch', 'log', 'logs', 'no_lock', 'writable_image',
                    'screenshots', 'shell', 'devices', 'gdbserver', 'update-images',
                         'clean-images']).intersection(self.commands))

    def needs_builder(self):
        return self.is_build_cmd()

    def needs_clickable_image(self):
        return (not self.is_custom_docker_image and
                not self.container_mode and
                (self.is_build_cmd() or
                    bool(set(
                        ['setup', 'run', 'ide', 'update-images',
                            'clean-images', 'gdb', 'gdbserver', 'review']
                    ).intersection(self.commands))))

    def needs_docker(self):
        return (not self.container_mode and
                (self.needs_clickable_image() or self.is_custom_docker_image))

    def check_clickable_version(self):
        migration_link = 'https://clickable-ut.dev/en/dev/migration.html'
        minimum_required = self.config['clickable_minimum_required']
        running_major = get_major_version()

        if self.config['clickable_minimum_required']:
            clickable_required_numbers = []

            if isinstance(self.config['clickable_minimum_required'], str):
                # Check if specified version string is valid
                if not re.fullmatch(r"\d+(\.\d+)*", self.config['clickable_minimum_required']):
                    raise ClickableException(
                        f'"{minimum_required}" specified as "clickable_minimum_required" is not a '
                        'valid version number'
                    )

                clickable_required_numbers = split_version_numbers(
                    minimum_required)
            else:
                value = self.config['clickable_minimum_required']
                clickable_required_numbers.append(int(value))
                fract = value % 1
                if fract:
                    # Get fract as integer without trailing zeros
                    clickable_required_numbers.append(int(f'{fract:f}'[2:].strip("0")))

            if is_newer_than_running(clickable_required_numbers):
                raise ClickableException(
                    f'This project requires Clickable version {minimum_required} '
                    f'({__version__} is used). Please update Clickable!')

            if clickable_required_numbers[0] < running_major:
                logger.warning('This project is configured for Clickable version %s according to '
                               'the "clickable_minimum_required" field. See %s for details about '
                               'migration to Clickable %s.', clickable_required_numbers[0],
                               migration_link, running_major)
        elif not self.is_project_independent_cmd():
            logger.warning('This project does not have a required Clickable version configured '
                           '("clickable_minimum_required"). See %s for details about migration to '
                           'Clickable %s if you run into issues.', migration_link, running_major)

    def check_arch_restrictions(self):
        if self.is_arch_agnostic():
            if self.config["arch"] != "all":
                raise ClickableException(
                    f'The "{self.config["builder"]}" builder needs architecture "all", but '
                    f'"{self.config["arch"]}" was specified')
            if (self.config["restrict_arch"] and
                    self.config["restrict_arch"] != "all"):
                raise ClickableException(
                    f'The "{self.config["builder"]}" builder needs architecture "all", but '
                    f'"restrict_arch" was set to "{self.config["restrict_arch"]}"')
        else:
            if self.is_desktop_mode():
                if self.config["arch"] != Constants.host_arch:
                    raise ClickableException(
                        f'Desktop mode needs host architecture "{Constants.host_arch}", but '
                        f'"{self.config["arch"]}" was specified'
                    )

        if (self.config['restrict_arch'] and
                self.config['restrict_arch'] != self.config['arch']):
            raise ClickableException(
                f'Cannot build app for architecture "{self.config["arch"]}" as it is restricted '
                f'to "{self.config["restrict_arch"]}" in the project config.'
            )

        if (self.config['restrict_arch_env'] and
                self.config['restrict_arch_env'] != self.config['arch'] and
                self.config['arch'] != 'all' and
                self.is_build_cmd()):
            raise ClickableException(
                f'Cannot build app for architecture "{self.config["arch"]}" as the environment is '
                f'restricted to "{self.config["restrict_arch_env"]}".'
            )

        if self.config['arch'] == 'all':
            install_keys = ['install_lib', 'install_bin', 'install_qml']
            for key in install_keys:
                if self.config[key]:
                    logger.warning(
                        "'%s' (%s) marked for install, even though architecture is 'all'.",
                        "', '".join(self.config[key]),
                        key
                    )
            if self.config['install_qml']:
                logger.warning(
                    "Be aware that QML modules are going to be installed to %s, which is not "
                    "part of 'QML2_IMPORT_PATH' at runtime.", self.config['app_qml_dir']
                )

    def check_paths(self):
        if (
            self.is_build_cmd() and
            os.path.normpath(self.cwd) == os.path.normpath(Constants.host_home)
        ):
            raise ClickableException(
                'Your are running a build command in your home directory.\nPlease navigate to '
                'an existing project or run "clickable create".'
            )

        if os.path.normpath(self.config['build_dir']) == os.path.normpath(self.config['root_dir']):
            raise ClickableException(
                'Your "build_dir" is configured to be the same as your project "root_dir".\n'
                'Please configure a sub-directory to avoid deleting your project on cleaning.'
            )

        if os.path.normpath(self.config['build_dir']) == os.path.normpath(self.config['src_dir']):
            raise ClickableException(
                'Your "build_dir" is configured to be the same as your "src_dir".\n'
                'Please configure different paths to avoid deleting your sources on cleaning.'
            )

    def check_builder_rules(self):
        if not self.needs_builder():
            return

        if self.config['builder'] == Constants.CUSTOM and not self.config['build']:
            raise ClickableException(
                'When using the "custom" builder you must specify a "build" in the config'
            )
        if self.config['builder'] == Constants.GO and not self.config['gopath']:
            raise ClickableException(
                'When using the "go" builder you must specify a "gopath" in the config or use the '
                '"GOPATH" env variable'
            )
        if self.config['builder'] == Constants.RUST and not self.config['cargo_home']:
            raise ClickableException(
                'When using the "rust" builder you must specify a "cargo_home" in the config'
            )

        if self.config['builder'] and self.config['builder'] not in Constants.builders:
            builders = ', '.join(Constants.builders)
            raise ClickableException(
                f'"{self.config["builder"]}" is not a valid builder ({builders})'
            )

    def check_desktop_configs(self):
        if self.is_desktop_mode():
            if self.use_nvidia and self.avoid_nvidia:
                raise ClickableException(
                    'Configuration conflict: enforcing and avoiding nvidia mode must not '
                    'be specified together.'
                )

    def check_path_sanity(self):
        for path in self.path_keys + self.absolute_path_keys:
            if self.config[path] and not is_path_sane(self.config[path]):
                raise ClickableException(
                    f'The "{path}" config contains special characters (e.g. spaces):\n'
                    f'{self.config[path]}'
                )

    def check_config_errors(self):
        self.check_clickable_version()
        self.check_arch_restrictions()
        self.check_builder_rules()
        self.check_desktop_configs()
        self.check_path_sanity()

    def is_foreign_target(self):
        return self.build_arch != Constants.host_arch

    def set_builder_interactive(self):
        if self.config['builder'] or not self.needs_builder():
            return

        if not self.interactive:
            raise ClickableException('No builder specified. Add a builder to your project config.')

        if not let_user_confirm(
                'No builder was specified, would you like to auto detect the builder?',
                default=False):
            raise ClickableException('Not builder configured. Is this a Clickable project?')

        builder = None
        directory = os.listdir(self.cwd)

        if 'config.xml' in directory:
            logger.warning(
                "This looks like a Cordova project. Cordova support was dropped in Clickable 8.")

        if not builder and 'CMakeLists.txt' in directory:
            builder = Constants.CMAKE

        pro_files = [f for f in directory if f.endswith('.pro')]
        if pro_files:
            builder = Constants.QMAKE

        if not builder:
            builder = Constants.PURE

        self.config['builder'] = builder

        logger.info('Auto detected builder to be "%s"', builder)
