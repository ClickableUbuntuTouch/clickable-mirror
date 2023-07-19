import os
import multiprocessing
import platform
from collections import OrderedDict

from clickable.utils import (
    merge_make_jobs_into_args,
    flexible_string_to_list,
    make_absolute,
)
from clickable.exceptions import ClickableException
from clickable.logger import logger

from .constants import Constants


class LibInitConfig:
    def __init__(self):
        self.name = None
        self.config_dict = None
        self.arch = None
        self.arch_inferred = False
        self.root_dir = None
        self.qt_version = None
        self.verbose = None
        self.libs_placeholders = None
        self.lib_configs = None
        self.cwd = None
        self.container_mode = None
        self.docker_image = None
        self.build_arch = None
        self.skip_image_setup = False


class LibConfig():
    config = {}

    static_placeholders = OrderedDict({
        "ARCH": "arch",
        "ARCH_TRIPLET": "arch_triplet",
        "ARCH_RUST": "arch_rust",
        "NAME": "name",
        "NUM_PROCS": "make_jobs",
        "ROOT": "root_dir",
        "BUILD_DIR": "build_dir",
        "SRC_DIR": "src_dir",
        "INSTALL_DIR": "install_dir",
    })
    accepts_placeholders = ["root_dir", "build_dir", "src_dir", "install_dir",
                            "cargo_home", "build",
                            "build_args", "make_args", "postmake", "postbuild",
                            "prebuild",
                            "env_vars", "build_home",
                            "dependencies_host", "dependencies_target", "dependencies_ppa",
                            "build"]

    path_keys = ['root_dir', 'build_dir', 'src_dir', 'install_dir',
                 'cargo_home', 'build_home']
    required = ['builder']
    # If specified as a string split at spaces
    flexible_split_list = ['dependencies_host', 'dependencies_target',
                           'dependencies_ppa', 'build_args', 'make_args']
    # If specified as a string convert it to a list of size 1
    flexible_list = ['prebuild', 'build', 'postmake', 'postbuild']
    builders = [Constants.QMAKE, Constants.CMAKE, Constants.CUSTOM]

    first_docker_info = True
    container_mode = False
    build_arch = None
    use_nvidia = False
    gopath = None
    verbose = False
    lib_configs = []

    def __init__(self, config):
        self.qt_version = config.qt_version
        self.verbose = config.verbose
        self.container_mode = config.container_mode
        self.build_arch = config.build_arch

        self.placeholders = {}
        self.placeholders.update(self.static_placeholders)
        self.placeholders.update(config.libs_placeholders)
        self.lib_configs = config.lib_configs
        self.cwd = config.cwd if config.cwd else os.getcwd()
        self.skip_image_setup = config.skip_image_setup

        self.set_host_arch()
        self.container_list = list(Constants.container_mapping[self.host_arch].values())

        self.config = {
            'name': config.name,
            'arch': config.arch,
            'restrict_arch': None,
            'arch_triplet': None,
            'arch_rust': Constants.rust_arch_target_mapping[self.build_arch],
            'builder': None,
            'postmake': None,
            'prebuild': None,
            'build': None,
            'postbuild': None,
            'build_dir': '${ROOT}/build/${ARCH_TRIPLET}/${NAME}',
            'build_home': '${BUILD_DIR}/.clickable/home',
            'src_dir': '${ROOT}/libs/${NAME}',
            'root_dir': config.root_dir,
            'dependencies_host': [],
            'dependencies_target': [],
            'dependencies_ppa': [],
            'make_jobs': None,
            'cargo_home': os.path.join(Constants.clickable_dir, 'cargo'),
            'docker_image': None,
            'build_args': [],
            'env_vars': {},
            'make_args': [],
            'install_dir': '${BUILD_DIR}/install',
            'image_setup': {},
            'test': None,
            'rust_channel': None,
        }

        self.config.update(config.config_dict)

        if self.config["restrict_arch"] == "host":
            self.config["restrict_arch"] = Constants.host_arch

        if config.arch_inferred and self.config["restrict_arch"]:
            self.config["arch"] = self.config["restrict_arch"]

        if self.config["docker_image"]:
            self.is_custom_docker_image = True
        else:
            self.is_custom_docker_image = False
            self.config["docker_image"] = config.docker_image

        self.cleanup_config()

        if self.config['arch'] not in Constants.arch_triplet_mapping:
            raise ClickableException(
                f'There is currently no support for architecture  "{self.config["arch"]}"'
            )

        self.config['arch_triplet'] = Constants.arch_triplet_mapping[self.config['arch']]

        for key in self.path_keys:
            if key not in self.accepts_placeholders and self.config[key]:
                self.config[key] = os.path.abspath(self.config[key])

        self.substitute_placeholders()

        self.check_config_errors()

        for key, value in self.config.items():
            logger.debug('Lib %s config value %s: %s', config.name, key, value)

    def __getattr__(self, name):
        return self.config[name]

    def __setattr__(self, name, value):
        if name in self.config:
            self.config[name] = value
        else:
            super().__setattr__(name, value)

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
                self.config[key] = [
                    val.replace(sub, rep) for val in self.config[key]
                ]
            else:
                self.config[key] = self.config[key].replace(sub, rep)

    def substitute_placeholders(self):
        for key in self.accepts_placeholders:
            for sub, placeholder in self.placeholders.items():
                rep = self.config[placeholder]
                self.substitute("${" + sub + "}", rep, key)
            if key in self.path_keys and self.config[key]:
                self.config[key] = make_absolute(self.config[key])

    def cleanup_config(self):
        for key in self.flexible_split_list:
            self.config[key] = flexible_string_to_list(self.config[key], split=True)

        for key in self.flexible_list:
            self.config[key] = flexible_string_to_list(self.config[key], split=False)

        if not self.config['make_jobs']:
            self.config['make_jobs'] = multiprocessing.cpu_count()

        self.config['make_args'] = merge_make_jobs_into_args(
            self.config['make_args'], self.config['make_jobs'])

        self.config['make_jobs'] = str(self.config['make_jobs'])

    def check_config_errors(self):
        if not self.config['builder']:
            raise ClickableException(
                f'The project config is missing a "builder" in library "{self.config["name"]}".'
            )

        if self.config['builder'] == Constants.CUSTOM and not self.config['build']:
            raise ClickableException(
                'When using the "custom" builder you must specify a "build" in one the lib configs'
            )

    def set_host_arch(self):
        host = platform.machine()
        self.host_arch = Constants.host_arch_mapping.get(host, None)

        if not self.host_arch:
            raise ClickableException(f"No support for host architecture {host}")

    def needs_clickable_image(self):
        return not self.container_mode and not self.is_custom_docker_image

    def needs_docker(self):
        return not self.container_mode

    def is_foreign_target(self):
        return self.build_arch != Constants.host_arch
