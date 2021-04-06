import os
import tarfile
import re

from clickable.logger import logger, Colors
from .idedelegate import IdeCommandDelegate

class AtomDelegate(IdeCommandDelegate):
    clickable_dir = os.path.expanduser('~/.clickable')
    project_path = os.getcwd()
    template_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'atom')
    pattern_cmake_vars = re.compile("set\(([-\w]+)\s+(.*)\)", flags=re.IGNORECASE)
    pattern_cmake_subvars = re.compile("\${([-\w]+)}")
    default_cmake_paths = {
        'CMAKE_INSTALL_DATADIR': 'share',
        'CMAKE_INSTALL_LIBDIR': 'lib',
        'CMAKE_INSTALL_BINDIR': 'bin',
    }


    def override_command(self, path):
        #atom does not launch within the bash process, but starts a decoupled process, making the bash command directly return causing clickable to close the docker container
        #to fix this it needs to be started with --wait parameter to wait for the process to finish before it returns. This way the container keeps running as long as atom runs.
        return path.replace('atom', "atom --wait .")

    def before_run(self, config, docker_config):

        #delete conflicting env vars in some cases
        docker_config.environment.pop("INSTALL_DIR", None)
        docker_config.environment.pop("APP_DIR", None)
        docker_config.environment.pop("SRC_DIR", None)
