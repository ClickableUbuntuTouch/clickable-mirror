import os
import tarfile
import re

from clickable.logger import logger, Colors
from .idedelegate import IdeCommandDelegate

class AtomDelegate(IdeCommandDelegate):
    clickable_dir = os.path.expanduser('~/.clickable')
    project_path = os.getcwd()
    template_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'atom')
    # init_settings_path = os.path.join(template_path, 'QtProject.tar.xz')
    # target_settings_path = os.path.join(clickable_dir,'QtProject')
    # template_path = os.path.join(template_path,'CMakeLists.txt.user.shared.in')
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


    def is_cmake_project(self):
         return os.path.isfile(os.path.join(self.project_path,'CMakeLists.txt'))

    #guess exec command and args from CMakeLists.txt
    # return None if nothing found
    def cmake_guess_exec_command(self, cmd_var):
        f = open(os.path.join(self.project_path,'CMakeLists.txt'), 'r')
        cmake_file =  f.read()
        output_cmd = None

        matches = self.pattern_cmake_vars.finditer(cmake_file)
        if matches:
            #store all cmake variable in a dictionnary
            cmake_vars = {}
            for k in matches:
                if k.group(1) not in cmake_vars:
                    value = k.group(2)
                    #strip quotes if any
                    if value.startswith('"'):
                        value = value[1:-1]
                    cmake_vars[k.group(1)] = value

            #try to find the exe command in cmake vars
            if cmd_var in cmake_vars:
                cmd = cmake_vars[cmd_var]
                #check if any vars in the exe command e.g "qmlscene ${MYVAR}" and replace them by their value
                output_cmd = self.recurse_replace(cmd, cmake_vars)

        return output_cmd

    #replace recursively cmakeLists.txt variable by their values
    def recurse_replace(self, cmd, cmake_vars):
        cmd_subvars = self.pattern_cmake_subvars.finditer(cmd)
        if cmd_subvars:
            for cmd_subvar in cmd_subvars:
                var = cmd_subvar.group(1)
                replacement = ''
                if var in cmake_vars:
                    replacement = cmake_vars[var]
                elif var in self.default_cmake_paths:
                    replacement = self.default_cmake_paths[var]

                if replacement != var:
                    cmd = cmd.replace('${'+ var +'}', replacement)
                    cmd = self.recurse_replace(cmd, cmake_vars)
        return cmd
