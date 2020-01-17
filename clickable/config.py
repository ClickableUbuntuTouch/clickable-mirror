import os
import json
import platform
import re
import xml.etree.ElementTree as ElementTree
from collections import OrderedDict

from clickable.system.queries.nvidia_drivers_in_use import NvidiaDriversInUse
from .libconfig import LibConfig

from .utils import (
    write_manifest,
    get_manifest,
    get_any_manifest,
    get_desktop,
    merge_make_jobs_into_args,
    flexible_string_to_list,
    env,
    FileNotFoundException,
    validate_clickable_json,
    make_absolute,
)
from .logger import logger, Colors
from clickable.exceptions import ClickableException


class Config(object):
    config = {}

    ENV_MAP = {
        'CLICKABLE_ARCH': 'arch',
        'CLICKABLE_TEMPLATE': 'template',
        'CLICKABLE_BUILD_DIR': 'build_dir',
        'CLICKABLE_DEFAULT': 'default',
        'CLICKABLE_MAKE_JOBS': 'make_jobs',
        'GOPATH': 'gopath',
        'CLICKABLE_DOCKER_IMAGE': 'docker_image',
        'CLICKABLE_BUILD_ARGS': 'build_args',
        'CLICKABLE_MAKE_ARGS': 'make_args',
        'CLICKABLE_DIRTY': 'dirty',
        'CLICKABLE_TEST': 'test',
    }

    PURE_QML_QMAKE = 'pure-qml-qmake'
    QMAKE = 'qmake'
    PURE_QML_CMAKE = 'pure-qml-cmake'
    CMAKE = 'cmake'
    CUSTOM = 'custom'
    CORDOVA = 'cordova'
    PURE = 'pure'
    PYTHON = 'python'
    GO = 'go'
    RUST = 'rust'

    templates = [PURE_QML_QMAKE, QMAKE, PURE_QML_CMAKE, CMAKE, CUSTOM, CORDOVA, PURE, PYTHON, GO, RUST]
    arch_agnostic_templates = [PURE_QML_QMAKE, PURE_QML_CMAKE, PURE]

    container_mapping = {
        ('16.04', 'armhf'): 'clickable/ubuntu-sdk:16.04-armhf',
        ('16.04', 'amd64'): 'clickable/ubuntu-sdk:16.04-amd64',
        ('16.04', 'amd64-nvidia'): 'clickable/ubuntu-sdk:16.04-amd64-nvidia',
        ('16.04', 'arm64'): 'clickable/ubuntu-sdk:16.04-arm64',
    }

    container_list = list(container_mapping.values())

    arch_triplet_mapping = {
        'armhf': 'arm-linux-gnueabihf',
        'arm64': 'aarch64-linux-gnu',
        'amd64': 'x86_64-linux-gnu',
        'all': 'all'
    }

    placeholders = OrderedDict({
        "ARCH_TRIPLET": "arch_triplet",
        "ROOT": "root_dir",
        "BUILD_DIR": "build_dir",
        "SRC_DIR": "src_dir",
        "INSTALL_DIR": "install_dir",
        "CLICK_LD_LIBRARY_PATH": "app_lib_dir",
        "CLICK_PATH": "app_bin_dir",
        "CLICK_QML2_IMPORT_PATH": "app_qml_dir",
    })
    accepts_placeholders = ["root_dir", "build_dir", "src_dir", "install_dir",
                            "gopath", "cargo_home", "scripts", "build",
                            "build_args", "make_args", "postmake", "postbuild",
                            "prebuild", "app_lib_dir", "app_bin_dir",
                            "install_lib", "install_qml", "install_bin",
                            "install_data", "app_qml_dir"]

    path_keys = ['root_dir', 'build_dir', 'src_dir', 'install_dir',
                 'cargo_home', 'gopath', 'app_lib_dir', 'app_bin_dir',
                 'app_qml_dir', 'install_lib', 'install_bin', 'install_qml',
                 'install_data']
    required = ['arch', 'build_dir', 'docker_image']
    flexible_lists = ['dependencies_build', 'dependencies_target',
                      'dependencies_ppa',
                      'install_lib', 'install_bin', 'install_qml',
                      'build_args', 'make_args', 'default', 'ignore']
    removed_keywords = ['chroot', 'sdk', 'package', 'app', 'premake', 'ssh',
                        'dependencies', 'specificDependencies', 'dir', 'lxd']

    first_docker_info = True
    device_serial_number = None
    ssh = None
    click_output = None
    container_mode = False
    use_nvidia = False
    avoid_nvidia = False
    apikey = None
    custom_docker_image = True
    verbose = False
    debug_build = False
    debug_gdb = False
    debug_gdb_port = None
    dark_mode = False
    desktop_device_home = os.path.expanduser('~/.clickable/home')
    desktop_locale = os.getenv('LANG', 'C')
    desktop_skip_build = False

    def __init__(self, args=None, clickable_version=None, desktop=False):
        # Must come after ARCH_TRIPLET to avoid breaking it
        self.placeholders.update({"ARCH": "arch"})

        self.desktop = desktop
        self.clickable_version = clickable_version
        self.cwd = os.getcwd()

        self.config = {
            'clickable_minimum_required': None,
            'arch': None,
            'arch_triplet': None,
            'template': None,
            'postmake': None,
            'prebuild': None,
            'build': None,
            'postbuild': None,
            'launch': None,
            'build_dir': '$ROOT/build/$ARCH_TRIPLET/app',
            'src_dir': '$ROOT',
            'root_dir': self.cwd,
            'kill': None,
            'scripts': {},
            'default': 'clean build install launch',
            'log': None,
            'dependencies_build': [],
            'dependencies_target': [],
            'dependencies_ppa': [],
            'install_lib': [],
            'install_bin': [],
            'install_qml': [],
            'install_data': {},
            'app_lib_dir': '$INSTALL_DIR/lib/$ARCH_TRIPLET',
            'app_bin_dir': '$INSTALL_DIR/lib/$ARCH_TRIPLET/bin',
            'app_qml_dir': '$INSTALL_DIR/lib/$ARCH_TRIPLET',
            'ignore': [],
            'make_jobs': 0,
            'gopath': None,
            'cargo_home': os.path.expanduser('~/.clickable/cargo'),
            'docker_image': None,
            'build_args': [],
            'env_vars': {},
            'make_args': [],
            'dirty': False,
            'libraries': {},
            'test': 'qmltestrunner',
            'install_dir': '$BUILD_DIR/install',
            'image_setup': {},
        }

        config_path = args.config if args else ''
        json_config = self.load_json_config(config_path)
        self.config.update(json_config)

        if args:
            self.detect_args_conflict(args)

        env_config = self.load_env_config()
        self.config.update(env_config)

        if args:
            arg_config = self.load_arg_config(args)
            self.config.update(arg_config)

        self.host_arch = platform.machine()
        self.is_arm = self.host_arch.startswith('arm')

        self.set_conditional_defaults()
        self.cleanup_config()

        if self.config['dirty'] and 'clean' in self.config['default']:
            self.config['default'].remove('clean')
        self.config['default'] = ' '.join(self.config['default'])

        self.set_build_arch()
        self.check_nvidia()

        if not self.config['docker_image']:
            self.custom_docker_image = False
            self.use_arch(self.build_arch)

        if self.config['arch'] not in self.arch_triplet_mapping:
            raise ClickableException('There currently is no support for {}'.format(self.config['arch']))
        self.config['arch_triplet'] = self.arch_triplet_mapping[self.config['arch']]

        self.setup_libs()

        for key in self.path_keys:
            if key not in self.accepts_placeholders and self.config[key]:
                self.config[key] = make_absolute(self.config[key])

        self.substitute_placeholders()
        self.set_env_vars()

        self.check_config_errors()

        for key, value in self.config.items():
            logger.debug('App config value {}: {}'.format(key, value))

    def set_conditional_defaults(self):
        if self.desktop:
            if self.config["arch"] and self.config["arch"] != "amd64":
                raise ClickableException('Desktop mode needs architecture "amd64", but "{}" was specified'.format(self.config["arch"]))
            self.config["arch"] = "amd64"
            logger.debug('Architecture set to "amd64" because of desktop mode.')

        if self.config["template"] in self.arch_agnostic_templates:
            self.config["arch"] = "all"
            logger.debug('Architecture set to "all" because template "{}" is architecture agnostic'.format(self.config['template']))

        if not self.config["arch"]:
            self.config["arch"] = "armhf"
            logger.debug('Architecture set to "armhf" because no architecture was specified')

    def use_arch(self, build_arch):
        if self.use_nvidia and not build_arch.endswith('-nvidia'):
            build_arch = "{}-nvidia".format(build_arch)

        if ('16.04', build_arch) not in self.container_mapping:
            raise ClickableException('There is currently no docker image for 16.04/{}'.format(build_arch))
        self.config['docker_image'] = self.container_mapping[('16.04', build_arch)]

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
            schema = {}
            try:
                return json.load(f)
            except ClickableException:
                raise ClickableException('Failed reading "clickable.schema", it is not valid json')
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
                except ClickableException:
                    raise ClickableException('Failed reading "clickable.json", it is not valid json')

                for key in self.removed_keywords:
                    if key in config_json:
                        raise ClickableException('"{}" is a no longer a valid configuration option'.format(key))

                schema = self.load_json_schema()
                validate_clickable_json(config=config_json, schema=schema)

                for key in self.config:
                    value = config_json.get(key, None)

                    if value:
                        config[key] = value
        elif not use_default_config:
            raise ClickableException('Specified config file {} does not exist.'.format(config_path))

        return config

    def load_env_config(self):
        if env('OPENSTORE_API_KEY'):
            self.apikey = env('OPENSTORE_API_KEY')

        if env('CLICKABLE_CONTAINER_MODE'):
            self.container_mode = True

        if env('CLICKABLE_SERIAL_NUMBER'):
            self.device_serial_number = env('CLICKABLE_SERIAL_NUMBER')

        if env('CLICKABLE_SSH'):
            self.ssh = env('CLICKABLE_SSH')

        if env('CLICKABLE_OUTPUT'):
            self.click_output = env('CLICKABLE_OUTPUT')

        if env('CLICKABLE_NVIDIA'):
            self.use_nvidia = True

        if env('CLICKABLE_NO_NVIDIA'):
            self.avoid_nvidia = True

        if env('CLICKABLE_DEBUG_BUILD'):
            self.debug_build = True

        if env('CLICKABLE_DARK_MODE'):
            self.dark_mode = True

        config = {}
        for var, name in self.ENV_MAP.items():
            if env(var):
                config[name] = env(var)

        return config

    def load_arg_config(self, args):
        if args.serial_number:
            self.device_serial_number = args.serial_number

        if args.ssh:
            self.ssh = args.ssh

        if args.output:
            self.click_output = args.output

        if args.container_mode:
            self.container_mode = args.container_mode

        if args.nvidia:
            self.use_nvidia = True

        if args.no_nvidia:
            self.avoid_nvidia = True

        if args.apikey:
            self.apikey = args.apikey

        if args.verbose:
            self.verbose = True

        if args.debug:
            self.debug_build = True

        if args.debug_build:
            self.debug_build = True
            logger.warning('"--debug-build" is deprecated, use "--debug" instead!')

        if args.gdb:
            self.debug_build = True
            self.debug_gdb = True

        if args.gdbserver:
            self.debug_build = True
            self.debug_gdb = True
            self.debug_gdb_port = args.gdbserver

        if args.dark_mode:
            self.dark_mode = True

        if args.lang:
            self.desktop_locale = args.lang

        config = {}
        if args.arch:
            config['arch'] = args.arch

        if args.docker_image:
            config['docker_image'] = args.docker_image

        if args.dirty:
            config['dirty'] = True

        if args.skip_build:
            self.desktop_skip_build = True

        return config

    def prepare_docker_env_vars(self):
        docker_env_vars = []
        for key, val in self.get_env_vars().items():
            docker_env_vars.append('-e {}="{}"'.format(key, val))

        return " ".join(docker_env_vars)

    def set_env_vars(self):
        os.environ.update(self.get_env_vars())

    def get_env_vars(self):
        env_vars = {}

        if self.debug_build:
            env_vars['DEBUG_BUILD'] = '1'

        for key, conf in self.placeholders.items():
            env_vars[key] = self.config[conf]

        env_vars.update(self.config['env_vars'])

        return env_vars

    def substitute_placeholders(self):
        for key in self.accepts_placeholders:
            for sub in self.placeholders:
                substitute = "$"+sub
                rep = self.config[self.placeholders[sub]]
                if self.config[key]:
                    if isinstance(self.config[key], dict):
                        self.config[key] = {k: val.replace(substitute, rep) for (k, val) in self.config[key].items()}
                    elif isinstance(self.config[key], list):
                        self.config[key] = [val.replace(substitute, rep) for val in self.config[key]]
                    else:
                        self.config[key] = self.config[key].replace(substitute, rep)
            if key in self.path_keys and self.config[key]:
                self.config[key] = make_absolute(self.config[key])

    def set_build_arch(self):
        if self.desktop or self.config['arch'] == 'all':
            self.build_arch = 'amd64'
        else:
            self.build_arch = self.config['arch']

    def check_nvidia(self):
        if self.desktop:
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
                self.debug_build
            ) for name, lib in self.config['libraries'].items()
        ]

        for lib in self.lib_configs:
            key = '{}_lib_install_dir'.format(lib.name)
            placeholder = '{}_LIB_INSTALL_DIR'.format(lib.name)
            self.config[key] = lib.install_dir
            self.placeholders.update({placeholder: key})

    def detect_args_conflict(self, args):
        if args.arch and self.config['arch'] and args.arch != self.config['arch']:
            raise ClickableException('Conflicting architectures "{}" (program argument) and "{}" (config) detected.'.format(args.arch, self.config["arch"]))

    def cleanup_config(self):
        self.make_args = merge_make_jobs_into_args(make_args=self.make_args, make_jobs=self.make_jobs)

        for key in self.flexible_lists:
            self.config[key] = flexible_string_to_list(self.config[key])

        if self.desktop_locale != "C" and "." not in self.desktop_locale:
            self.desktop_locale = "{}.UTF-8".format(self.desktop_locale)

        if not self.config['kill']:
            if self.config['template'] == self.CORDOVA:
                self.config['kill'] = 'cordova-ubuntu'
            elif self.config['template'] == self.PURE_QML_CMAKE or self.config['template'] == self.PURE_QML_QMAKE or self.config['template'] == self.PURE:
                self.config['kill'] = 'qmlscene'
            else:
                try:
                    desktop = get_desktop(self.cwd)
                except ClickableException:
                    desktop = None
                except Exception:
                    logger.debug('Unable to load or parse desktop file', exc_info=e)
                    desktop = None

                if desktop and 'Exec' in desktop:
                    self.config['kill'] = desktop['Exec'].replace('%u', '').replace('%U', '').strip()

        if self.desktop:
            self.config['dependencies_build'] += self.config['dependencies_target']
            self.config['dependencies_target'] = []

        self.ignore.extend(['.git', '.bzr'])

        if self.config['arch'] == 'all':
            self.config['app_lib_dir'] = '$INSTALL_DIR/lib'
            self.config['app_bin_dir'] = '$INSTALL_DIR'
            self.config['app_qml_dir'] = '$INSTALL_DIR/qml'


    def check_config_errors(self):
        if self.config['clickable_minimum_required']:
            # Check if specified version string is valid
            if not re.fullmatch("\d+(\.\d+)*", self.config['clickable_minimum_required']):
                raise ClickableException('"{}" specified as "clickable_minimum_required" is not a valid version number'.format(self.config['clickable_minimum_required']))

            # Convert version strings to integer lists
            clickable_version_numbers = [int(n) for n in re.split('\.', self.clickable_version)]
            clickable_required_numbers = [int(n) for n in re.split('\.', self.config['clickable_minimum_required'])]
            if len(clickable_required_numbers) > len(clickable_version_numbers):
                logger.warning('Clickable version number only consists of {} numbers, but {} numbers specified in "clickable_minimum_required". Superfluous numbers will be ignored.'.format(len(clickable_version_numbers), len(clickable_required_numbers)))

            # Compare all numbers until finding an unequal pair
            for req, ver in zip(clickable_required_numbers, clickable_version_numbers):
                if req < ver:
                    break
                if req > ver:
                    raise ClickableException('This project requires Clickable version {} ({} is used). Please update Clickable!'.format(self.config['clickable_minimum_required'], self.clickable_version))

        if self.custom_docker_image:
            if self.dependencies_build or self.dependencies_target or self.dependencies_ppa:
                logger.warning("Dependencies are ignored when using a custom docker image!")
            if self.image_setup:
                logger.warning("Docker image setup is ignored when using a custom docker image!")

        if self.config['arch'] == 'all':
            install_keys = ['install_lib', 'install_bin', 'install_qml']
            for key in install_keys:
                if self.config[key]:
                    logger.warning("'{}' ({}) marked for install, even though architecture is 'all'.".format("', '".join(self.config[key]), key))
            if self.config['install_qml']:
                logger.warning("Be aware that QML modules are going to be installed to {}, which is not part of 'QML2_IMPORT_PATH' at runtime.".format(self.config['app_qml_dir']))

        if self.debug_gdb and not self.desktop:
            raise ClickableException("GDB debugging is only supported in desktop mode! Consider running 'clickable desktop --gdb'")

        if self.config['template'] == self.CUSTOM and not self.config['build']:
            raise ClickableException('When using the "custom" template you must specify a "build" in the config')
        if self.config['template'] == self.GO and not self.config['gopath']:
            raise ClickableException('When using the "go" template you must specify a "gopath" in the config or use the '
                             '"GOPATH"env variable')
        if self.config['template'] == self.RUST and not self.config['cargo_home']:
            raise ClickableException('When using the "rust" template you must specify a "cargo_home" in the config')

        if self.config['template'] and self.config['template'] not in self.templates:
            raise ClickableException('"{}" is not a valid template ({})'.format(self.config['template'], ', '.join(self.templates)))

        if self.desktop:
            if self.use_nvidia and self.avoid_nvidia:
                raise ClickableException('Configuration conflict: enforcing and avoiding nvidia mode must not be specified together.')

        # if self.config['arch'] != 'all' and self.config['template'] in self.arch_agnostic_templates:
        #     raise ClickableException('The "{}" build template needs architecture "all", but "{}" was specified'.format(
        #         self.config['template'],
        #         self.config['arch'],
        #     ))

        for key in self.required:
            if key not in self.config:
                raise ClickableException('"{}" is empty in the config file'.format(key))

    def get_template(self):
        if not self.config['template']:
            choice = input(
                Colors.INFO + 'No build template was specified, would you like to auto detect the template [y/N]: ' + Colors.CLEAR
            ).strip().lower()
            if choice != 'y' and choice != 'yes':
                raise ClickableException('Not auto detecting build template')

            template = None
            directory = os.listdir(os.getcwd())

            if 'config.xml' in directory:
                template = Config.CORDOVA

            if not template:
                try:
                    manifest = get_any_manifest(os.getcwd())
                except ClickableException:
                    manifest = None

            if not template and 'CMakeLists.txt' in directory:
                template = Config.CMAKE

                if manifest and manifest.get('architecture', None) == 'all':
                    template = Config.PURE_QML_CMAKE

            pro_files = [f for f in directory if f.endswith('.pro')]

            if pro_files:
                template = Config.QMAKE

                if manifest and manifest.get('architecture', None) == 'all':
                    template = Config.PURE_QML_QMAKE

            if not template:
                template = Config.PURE

            self.config['template'] = template
            self.cleanup_config()

            logger.info('Auto detected template to be "{}"'.format(template))

        return self.config['template']

    def write_manifest(self, manifest):
        return write_manifest(self.install_dir, manifest)

    def get_manifest(self):
        return get_manifest(self.install_dir)

    def find_version(self):
        if self.config['template'] == Config.CORDOVA:
            tree = ElementTree.parse('config.xml')
            root = tree.getroot()
            version = root.attrib['version'] if 'version' in root.attrib else '1.0.0'
        else:
            version = self.get_manifest().get('version', '1.0')

        return version

    def find_package_name(self):
        if self.config['template'] == Config.CORDOVA:
            tree = ElementTree.parse('config.xml')
            root = tree.getroot()
            package = root.attrib['id'] if 'id' in root.attrib else None

            if not package:
                raise ClickableException('No package name specified in config.xml')

        else:
            package = self.get_manifest().get('name', None)

            if not package:
                raise ClickableException('No package name specified in manifest.json or clickable.json')

        return package

    def find_package_title(self):
        if self.config['template'] == Config.CORDOVA:
            tree = ElementTree.parse('config.xml')
            root = tree.getroot()
            title = root.attrib['name'] if 'name' in root.attrib else None

            if not title:
                raise ClickableException('No package title specified in config.xml')

        else:
            title = self.get_manifest().get('title', None)

            if not title:
                raise ClickableException(
                    'No package title specified in manifest.json or clickable.json')

        return title

    def find_app_name(self):
        app = None
        hooks = self.get_manifest().get('hooks', {})
        for key, value in hooks.items():
            if 'desktop' in value:
                app = key
                break

        if not app:  # If we don't find an app with a desktop file just find the first one
            apps = list(hooks.keys())
            if len(apps) > 0:
                app = apps[0]

        if not app:
            raise ClickableException('No app name specified in manifest.json')

        return app

    def get_click_filename(self):
        self.get_template()

        return '{}_{}_{}.click'.format(self.find_package_name(), self.find_version(), self.config['arch'])
