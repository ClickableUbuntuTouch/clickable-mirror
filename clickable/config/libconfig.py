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
        self.name = None,
        self.json_config = None,
        self.arch = None,
        self.root_dir = None,
        self.qt_version = None,
        self.verbose = None
        self.libs_placeholders = None


class LibConfig():
    cwd = os.getcwd()
    config = {}

    static_placeholders = OrderedDict({
        "ARCH": "arch",
        "ARCH_TRIPLET": "arch_triplet",
        "NAME": "name",
        "ROOT": "root_dir",
        "BUILD_DIR": "build_dir",
        "SRC_DIR": "src_dir",
        "INSTALL_DIR": "install_dir",
    })
    accepts_placeholders = ["root_dir", "build_dir", "src_dir", "install_dir",
                            "build",
                            "build_args", "make_args", "postmake", "postbuild",
                            "prebuild",
                            "env_vars", "build_home"]

    path_keys = ['root_dir', 'build_dir', 'src_dir', 'install_dir',
                 'build_home']
    required = ['builder']
    # If specified as a string split at spaces
    flexible_split_list = ['dependencies_host', 'dependencies_target',
                           'dependencies_ppa', 'build_args', 'make_args']
    # If specified as a string convert it to a list of size 1
    flexible_list = ['prebuild', 'build', 'postmake', 'postbuild']
    builders = [Constants.QMAKE, Constants.CMAKE, Constants.CUSTOM]

    first_docker_info = True
    container_mode = False
    use_nvidia = False
    gopath = None
    verbose = False

    def __init__(self, config):
        self.qt_version = config.qt_version
        self.verbose = config.verbose
        self.placeholders = {}
        self.placeholders.update(self.static_placeholders)
        self.placeholders.update(config.libs_placeholders)

        self.set_host_arch()
        self.container_list = list(Constants.container_mapping[self.host_arch].values())

        self.config = {
            'name': config.name,
            'arch': config.arch,
            'arch_triplet': None,
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
            'docker_image': None,
            'build_args': [],
            'env_vars': {},
            'make_args': [],
            'install_dir': '${BUILD_DIR}/install',
            'image_setup': {},
            'test': 'ctest',
        }

        self.config.update(config.json_config)
        if self.config["docker_image"]:
            self.is_custom_docker_image = True
        else:
            self.is_custom_docker_image = False

        self.cleanup_config()

        self.config['arch_triplet'] = Constants.arch_triplet_mapping[self.config['arch']]

        for key in self.path_keys:
            if key not in self.accepts_placeholders and self.config[key]:
                self.config[key] = os.path.abspath(self.config[key])

        self.substitute_placeholders()
        self.set_env_vars()

        self.check_config_errors()

        for key, value in self.config.items():
            logger.debug('Lib {} config value {}: {}'.format(config.name, key, value))

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
            docker_env_vars.append('-e {}="{}"'.format(key, val))

        return " ".join(docker_env_vars)

    def set_env_vars(self):
        os.environ.update(self.get_env_vars())

    def get_env_vars(self):
        env_vars = {}

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
            for sub in self.placeholders:
                rep = self.config[self.placeholders[sub]]
                self.substitute("${"+sub+"}", rep, key)
            if key in self.path_keys and self.config[key]:
                self.config[key] = make_absolute(self.config[key])

    def cleanup_config(self):
        if not self.config['make_jobs']:
            self.config['make_jobs'] = multiprocessing.cpu_count()
        self.make_args = merge_make_jobs_into_args(
            make_args=self.make_args, make_jobs=self.make_jobs)

        for key in self.flexible_split_list:
            self.config[key] = flexible_string_to_list(self.config[key], split=True)

        for key in self.flexible_list:
            self.config[key] = flexible_string_to_list(self.config[key], split=False)

    def check_config_errors(self):
        if not self.config['builder']:
            raise ClickableException(
                'The clickable.json is missing a "builder" in library "{}".'.format(
                    self.config["name"]
                )
            )

        if self.config['builder'] == Constants.CUSTOM and not self.config['build']:
            raise ClickableException(
                'When using the "custom" builder you must specify a "build" in one the lib configs'
            )

        if self.is_custom_docker_image:
            if self.dependencies_host or self.dependencies_target or self.dependencies_ppa:
                logger.warning(
                    "Dependencies are ignored when using a custom docker image!")
            if self.image_setup:
                logger.warning(
                    "Docker image setup is ignored when using a custom docker image!")

    def set_host_arch(self):
        host = platform.machine()
        self.host_arch = Constants.host_arch_mapping.get(host, None)

        if not self.host_arch:
            raise ClickableException("No support for host architecture {}".format(host))

    def needs_clickable_image(self):
        return not self.container_mode and not self.is_custom_docker_image

    def needs_docker(self):
        return not self.container_mode
