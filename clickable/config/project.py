import os
import json
import platform
import re
import multiprocessing
from collections import OrderedDict

from clickable.system.queries.nvidia_drivers_in_use import NvidiaDriversInUse
from clickable.version import __version__
from clickable.exceptions import ClickableException

from .libconfig import LibConfig
from .file_helpers import InstallFiles, ProjectFiles
from .constants import Constants

from ..utils import (
    merge_make_jobs_into_args,
    get_make_jobs_from_args,
    flexible_string_to_list,
    env,
    validate_clickable_json,
    make_absolute,
    make_env_var_conform,
    let_user_confirm,
)
from ..logger import logger


class ProjectConfig():
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
                            "prebuild", "rustup_home",
                            "install_lib", "install_qml", "install_bin",
                            "install_data", "env_vars", "build_home"]

    path_keys = ['root_dir', 'build_dir', 'src_dir', 'install_dir',
                 'cargo_home', 'gopath', 'app_lib_dir', 'app_bin_dir',
                 'app_qml_dir', 'build_home', 'rustup_home']
    # If specified as a string split at spaces
    flexible_split_list = ['dependencies_host', 'dependencies_target',
                           'dependencies_ppa', 'install_lib', 'install_bin',
                           'install_qml', 'build_args', 'make_args', 'default',
                           'ignore']
    # If specified as a string convert it to a list of size 1
    flexible_list = ['prebuild', 'build', 'postmake', 'postbuild']
    removed_keywords = ['chroot', 'sdk', 'package', 'app', 'premake', 'ssh',
                        'dependencies', 'specificDependencies', 'dir', 'lxd',
                        'arch', 'template', 'dependencies_build', 'dirty']

    first_docker_info = True
    device_serial_number = None
    ssh = None
    container_mode = False
    use_nvidia = False
    avoid_nvidia = False
    verbose = False
    interactive = True
    build_arch = None
    container_list = []
    install_files = []
    lib_configs = []

    def __init__(self, args=None, cwd=None, commands=None, always_clean=False):
        if not commands:
            commands = []

        self.placeholders = {}
        self.placeholders.update(ProjectConfig.static_placeholders)

        if not Constants.host_arch:
            raise ClickableException(
                "No support for host architecture {}".format(platform.machine())
            )
        self.cwd = cwd if cwd else os.getcwd()
        self.project_files = ProjectFiles(self.cwd)

        self.set_default_config()
        self.parse_configs(args, commands, always_clean)
        self.check_paths()
        self.set_builder_interactive()
        self.set_conditional_defaults()
        self.setup()
        self.check_config_errors()

    def set_default_config(self):
        self.config = {
            'clickable_minimum_required': None,
            'arch': None,
            'restrict_arch_env': None,
            'restrict_arch': None,
            'arch_triplet': None,
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
            'default': 'build install launch',
            'log': None,
            'dependencies_host': [],
            'dependencies_target': [],
            'dependencies_ppa': [],
            'install_lib': [],
            'install_bin': [],
            'install_qml': [],
            'install_data': {},
            'app_lib_dir': '${INSTALL_DIR}/lib/${ARCH_TRIPLET}',
            'app_bin_dir': '${INSTALL_DIR}/lib/${ARCH_TRIPLET}/bin',
            'app_qml_dir': '${INSTALL_DIR}/lib/${ARCH_TRIPLET}',
            'ignore': [],
            'make_jobs': None,
            'gopath': None,
            'cargo_home': os.path.expanduser('~/.clickable/cargo'),
            'rustup_home': os.path.expanduser('~/.clickable/rustup'),
            'docker_image': None,
            'build_args': [],
            'env_vars': {},
            'env_env_vars': {},
            'make_args': [],
            'libraries': {},
            'test': 'qmltestrunner',
            'install_dir': '${BUILD_DIR}/install',
            'image_setup': {},
            'qt_version': Constants.default_qt,
            'framework': None,
            'always_clean': False,
        }

    def parse_configs(self, args, commands, always_clean):
        config_path = args.config if args else None
        json_config = self.load_json_config(config_path)

        self.config.update(json_config)
        env_config = self.load_env_config()
        self.config.update(env_config)
        self.config['env_vars'].update(self.config['env_env_vars'])

        if args:
            arg_config = self.load_arg_config(args)
            self.config.update(arg_config)

        self.config['default'] = flexible_string_to_list(self.config['default'], split=True)

        self.commands = commands
        if always_clean:
            self.config['always_clean'] = True

        if not self.commands:
            self.commands = self.config['default']

        if (
            self.config['always_clean']
            and self.is_app_build_cmd()
            and self.commands[0] != 'clean'
        ):
            self.commands = ['clean'] + self.commands

    def setup(self):
        self.cleanup_config()

        self.setup_image()
        self.setup_libs()
        self.handle_path_keys_and_placeholders()

        self.setup_helpers()
        self.set_env_vars()

        for key, value in self.config.items():
            logger.debug('App config value {}: {}'.format(key, value))

    def set_conditional_defaults(self):
        if self.config["docker_image"]:
            self.is_custom_docker_image = True
        else:
            self.is_custom_docker_image = False

        if not self.config["arch"]:
            if self.is_arch_agnostic():
                self.config["arch"] = "all"
                logger.debug(
                    'Architecture set to "all" because builder "{}" is architecture '
                    'agnostic'.format(self.config['builder'])
                )
            elif self.is_desktop_mode():
                self.config["arch"] = Constants.host_arch
                logger.debug(
                    'Architecture set to "{}" because of desktop mode.'.format(self.config["arch"])
                )
            elif self.config["restrict_arch"]:
                self.config["arch"] = self.config["restrict_arch"]
            elif self.config["restrict_arch_env"]:
                self.config["arch"] = self.config["restrict_arch_env"]
                logger.debug(
                    'Architecture set to "{}" due to environment restriction'
                    .format(self.config["arch"])
                )
            elif self.container_mode:
                self.config['arch'] = Constants.host_arch
                logger.debug(
                    'Architecture set to "{}" due to container mode'.format(self.config['arch'])
                )
            else:
                self.config['arch'] = 'armhf'
                logger.debug(
                    'Architecture set to "{}" because no architecture was '
                    'specified'.format(self.config['arch'])
                )

        if self.config['arch'] == 'all':
            self.config['app_lib_dir'] = '${INSTALL_DIR}/lib'
            self.config['app_bin_dir'] = '${INSTALL_DIR}'
            self.config['app_qml_dir'] = '${INSTALL_DIR}/qml'

        if self.config['arch'] not in Constants.arch_triplet_mapping:
            raise ClickableException(
                'There is currently no support for architecture  "{}"'.format(self.config['arch'])
            )
        self.config['arch_triplet'] = Constants.arch_triplet_mapping[self.config['arch']]

        if Constants.host_arch not in Constants.container_mapping:
            raise ClickableException(
                'Clickable currently does not have docker images for your host '
                'architecture "{}"'.format(Constants.host_arch)
            )

        if not self.config['kill']:
            if self.config['builder'] == Constants.CORDOVA:
                self.config['kill'] = 'cordova-ubuntu'
            elif (
                self.config['builder'] == Constants.PURE_QML_CMAKE or
                self.config['builder'] == Constants.PURE_QML_QMAKE or
                self.config['builder'] == Constants.PURE
            ):
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
                raise ClickableException('Qt version "{}" is not known to Clickable'.format(qt))

            self.config['framework'] = framework

    def setup_image(self):
        self.set_build_arch()

        if self.needs_clickable_image():
            self.check_nvidia_mode()

            if self.use_nvidia and not self.build_arch.endswith('-nvidia'):
                if self.is_ide_command():
                    self.build_arch = "{}-nvidia-ide".format(self.build_arch)
                else:
                    self.build_arch = "{}-nvidia".format(self.build_arch)

            if self.is_ide_command() and not self.use_nvidia:
                self.build_arch = "{}-ide".format(self.build_arch)

            image_framework = Constants.framework_image_mapping.get(
                    self.config['framework'], Constants.framework_fallback)

            container_mapping_host = Constants.container_mapping[Constants.host_arch]
            if (image_framework, self.build_arch) not in container_mapping_host:
                raise ClickableException(
                    'There is currently no docker image for {}/{}'.format(
                        image_framework,
                        self.build_arch
                    )
                )
            self.config['docker_image'] = container_mapping_host[
                (image_framework, self.build_arch)
            ]
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

    def load_json_schema(self):
        schema_path = os.path.join(os.path.dirname(__file__), 'clickable.schema')
        with open(schema_path, 'r') as f:
            try:
                return json.load(f)
            except ValueError as err:
                raise ClickableException(
                    'Failed reading "clickable.schema", it is not valid json'
                ) from err
            return None

    def load_json_config(self, config_path):
        config = {}
        use_default_config = not config_path
        if use_default_config:
            config_path = os.path.join(self.cwd, 'clickable.json')

        if os.path.isfile(config_path):
            with open(config_path, 'r') as f:
                config_json = {}
                try:
                    config_json = json.load(f)
                except ValueError as err:
                    raise ClickableException(
                        'Failed reading "clickable.json", it is not valid json'
                    ) from err

                for key in self.removed_keywords:
                    if key in config_json:
                        raise ClickableException(
                            '"{}" is no longer a valid configuration option'.format(key)
                        )

                schema = self.load_json_schema()
                validate_clickable_json(config=config_json, schema=schema)

                for key in self.config:
                    value = config_json.get(key, None)

                    if value:
                        config[key] = value
        elif not use_default_config:
            raise ClickableException(
                'Specified config file {} does not exist.'.format(config_path)
            )

        return config

    def load_env_config(self):
        if self.get_env_var('CLICKABLE_CONTAINER_MODE'):
            self.container_mode = True

        if self.get_env_var('CLICKABLE_SERIAL_NUMBER'):
            self.device_serial_number = self.get_env_var('CLICKABLE_SERIAL_NUMBER')

        if self.get_env_var('CLICKABLE_SSH'):
            self.ssh = self.get_env_var('CLICKABLE_SSH')

        if self.get_env_var('CLICKABLE_NVIDIA'):
            self.use_nvidia = True

        if self.get_env_var('CLICKABLE_NO_NVIDIA'):
            self.avoid_nvidia = True

        if self.get_env_var('CLICKABLE_NON_INTERACTIVE'):
            self.interactive = False

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
        if args.serial_number:
            self.device_serial_number = args.serial_number

        if args.ssh:
            self.ssh = args.ssh

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

        return config

    def prepare_docker_env_vars(self):
        docker_env_vars = []
        env_dict = self.get_env_vars()

        env_dict["HOME"] = self.config["build_home"]

        for key, val in env_dict.items():
            docker_env_vars.append('-e {}="{}"'.format(key, val))

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

    def substitute(self, sub, rep, key):
        if self.config[key]:
            if isinstance(self.config[key], dict):
                self.config[key] = {
                    k: val.replace(sub, rep) for (k, val) in self.config[key].items()
                }
            elif isinstance(self.config[key], list):
                self.config[key] = [val.replace(sub, rep) for val in self.config[key]]
            else:
                self.config[key] = self.config[key].replace(sub, rep)

    def handle_path_keys_and_placeholders(self):
        for key in self.path_keys:
            if key not in self.accepts_placeholders and self.config[key]:
                self.config[key] = make_absolute(self.config[key])

        for key in self.accepts_placeholders:
            for sub in self.placeholders:
                rep = self.config[self.placeholders[sub]]
                self.substitute("${"+sub+"}", rep, key)
            if key in self.path_keys and self.config[key]:
                self.config[key] = make_absolute(self.config[key])

    def set_build_arch(self):
        if self.config['arch'] == 'all':
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
        self.lib_configs = [
            LibConfig(
                name,
                lib,
                self.config['arch'],
                self.config['root_dir'],
                self.config['qt_version'],
                self.verbose,  # TODO check whether verbosity is handled by this config
            ) for name, lib in self.config['libraries'].items()
        ]

        for lib in self.lib_configs:
            name_conform = make_env_var_conform(lib.name)
            key = '{}_lib_install_dir'.format(name_conform)
            placeholder = '{}_LIB_INSTALL_DIR'.format(name_conform)
            self.config[key] = lib.install_dir
            self.placeholders.update({placeholder: key})

            for lp in self.libs_placeholders:
                key = '{}_LIB_{}'.format(lib.name, lp)
                placeholder = make_env_var_conform(key)
                self.placeholders[placeholder] = key
                self.config[key] = lib.config[lp]

    def cleanup_config(self):
        for key in self.flexible_split_list:
            self.config[key] = flexible_string_to_list(self.config[key], split=True)

        for key in self.flexible_list:
            self.config[key] = flexible_string_to_list(self.config[key], split=False)

        self.ignore.extend(['.git', '.bzr', '.clickable'])

        self.config['default'] = ' '.join(self.config['default'])

    def is_desktop_mode(self):
        return bool(set(['desktop', 'test-libs', 'test', 'ide']).intersection(self.commands))

    def is_ide_command(self):
        return "ide" in self.commands

    def is_app_build_cmd(self):
        return self.is_desktop_mode() or 'build' in self.commands

    def is_build_cmd(self):
        return self.is_app_build_cmd() or 'build-libs' in self.commands

    def needs_builder(self):
        return self.is_build_cmd()

    def needs_clickable_image(self):
        return (not self.is_custom_docker_image and
                not self.container_mode and
                (self.is_build_cmd() or
                    bool(set(
                        ['setup', 'run', 'ide', 'update', 'gdb', 'gdbserver', 'review']
                    ).intersection(self.commands))))

    def needs_docker(self):
        return (not self.container_mode and
                (self.needs_clickable_image() or self.is_custom_docker_image))

    def check_clickable_version(self):
        if self.config['clickable_minimum_required']:
            # Check if specified version string is valid
            if not re.fullmatch(r"\d+(\.\d+)*", self.config['clickable_minimum_required']):
                raise ClickableException(
                    '"{}" specified as "clickable_minimum_required" is not a valid '
                    'version number'.format(self.config['clickable_minimum_required'])
                )

            # Convert version strings to integer lists
            clickable_version_numbers = [int(n) for n in re.split(r'\.', __version__)]
            clickable_required_numbers = [
                int(n) for n in re.split(r'\.', self.config['clickable_minimum_required'])
            ]
            if len(clickable_required_numbers) > len(clickable_version_numbers):
                logger.warning(
                    'Clickable version number only consists of {} numbers, but {} '
                    'numbers specified in "clickable_minimum_required". Superfluous numbers '
                    'will be ignored.'.format(
                        len(clickable_version_numbers),
                        len(clickable_required_numbers)
                    )
                )

            # Compare all numbers until finding an unequal pair
            for req, ver in zip(clickable_required_numbers, clickable_version_numbers):
                if req < ver:
                    break
                if req > ver:
                    raise ClickableException(
                        'This project requires Clickable version {} ({} is used). '
                        'Please update Clickable!'.format(
                            self.config['clickable_minimum_required'],
                            __version__
                        )
                    )

    def check_arch_restrictions(self):
        if self.is_arch_agnostic():
            if self.config["arch"] != "all":
                raise ClickableException(
                    'The "{}" builder needs architecture "all", but "{}" was specified'.format(
                        self.config['builder'],
                        self.config['arch'],
                    )
                )
            if (self.config["restrict_arch"] and
                    self.config["restrict_arch"] != "all"):
                raise ClickableException(
                    'The "{}" builder needs architecture "all", but "restrict_arch" was set '
                    'to "{}"'.format(
                        self.config['builder'],
                        self.config['restrict_arch'],
                    )
                )
        else:
            if self.is_desktop_mode():
                if self.config["arch"] != Constants.host_arch:
                    raise ClickableException(
                        'Desktop mode needs host architecture "{}", but "{}" was '
                        'specified'.format(Constants.host_arch, self.config["arch"])
                    )

        if (self.config['restrict_arch'] and
                self.config['restrict_arch'] != self.config['arch']):
            raise ClickableException(
                'Cannot build app for architecture "{}" as it is restricted to "{}" '
                'in the clickable.json.'.format(self.config["arch"], self.config['restrict_arch'])
            )

        if (self.config['restrict_arch_env'] and
                self.config['restrict_arch_env'] != self.config['arch'] and
                self.config['arch'] != 'all' and
                self.is_build_cmd()):
            raise ClickableException(
                'Cannot build app for architecture "{}" as the environment is restricted '
                'to "{}".'.format(self.config["arch"], self.config['restrict_arch_env'])
            )

        if self.config['arch'] == 'all':
            install_keys = ['install_lib', 'install_bin', 'install_qml']
            for key in install_keys:
                if self.config[key]:
                    logger.warning(
                        "'{}' ({}) marked for install, even though architecture is 'all'.".format(
                            "', '".join(self.config[key]),
                            key
                        )
                    )
            if self.config['install_qml']:
                logger.warning(
                    "Be aware that QML modules are going to be installed to {}, which is not "
                    "part of 'QML2_IMPORT_PATH' at runtime.".format(self.config['app_qml_dir'])
                )

    def check_paths(self):
        if (
            self.is_build_cmd() and
            os.path.normpath(self.cwd) == os.path.normpath(os.path.expanduser('~'))
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
            raise ClickableException(
                '"{}" is not a valid builder ({})'.format(
                    self.config['builder'],
                    ', '.join(Constants.builders)
                )
            )

    def check_docker_configs(self):
        if self.is_custom_docker_image:
            if self.dependencies_host or self.dependencies_target or self.dependencies_ppa:
                logger.warning("Dependencies are ignored when using a custom docker image!")
            if self.image_setup:
                logger.warning("Docker image setup is ignored when using a custom docker image!")

    def check_desktop_configs(self):
        if self.is_desktop_mode():
            if self.use_nvidia and self.avoid_nvidia:
                raise ClickableException(
                    'Configuration conflict: enforcing and avoiding nvidia mode must not '
                    'be specified together.'
                )

            if self.container_mode:
                raise ClickableException('Desktop Mode in Container Mode is not supported.')

    def check_config_errors(self):
        self.check_clickable_version()
        self.check_arch_restrictions()
        self.check_builder_rules()
        self.check_docker_configs()
        self.check_desktop_configs()

    def set_builder_interactive(self):
        if self.config['builder'] or not self.needs_builder():
            return

        if not self.interactive:
            raise ClickableException('No builder specified. Add a builder to your clickable.json.')

        if not let_user_confirm(
                'No builder was specified, would you like to auto detect the builder?',
                default=False):
            raise ClickableException('Not builder configured. Is this a Clickable project?')

        builder = None
        directory = os.listdir(os.getcwd())

        if 'config.xml' in directory:
            builder = Constants.CORDOVA

        if not builder and 'CMakeLists.txt' in directory:
            builder = Constants.CMAKE

        pro_files = [f for f in directory if f.endswith('.pro')]
        if pro_files:
            builder = Constants.QMAKE

        if not builder:
            builder = Constants.PURE

        self.config['builder'] = builder

        logger.info('Auto detected builder to be "{}"'.format(builder))
