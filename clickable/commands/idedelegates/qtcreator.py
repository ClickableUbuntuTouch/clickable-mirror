import os
import tarfile
import re

from clickable.config.constants import Constants
from clickable.logger import logger
from .idedelegate import IdeCommandDelegate


class QtCreatorDelegate(IdeCommandDelegate):
    project_path = os.getcwd()
    template_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'qtcreator')
    init_settings_path = os.path.join(template_path, 'QtProject.tar.xz')
    target_settings_path = os.path.join(Constants.clickable_dir, 'QtProject')
    template_path = os.path.join(template_path, 'CMakeLists.txt.user.shared.in')
    pattern_cmake_vars = re.compile(r"set\(([-\w]+)\s+(.*)\)", flags=re.IGNORECASE)
    pattern_cmake_subvars = re.compile(r"\${([-\w]+)}")
    default_cmake_paths = {
        'CMAKE_INSTALL_DATADIR': 'share',
        'CMAKE_INSTALL_LIBDIR': 'lib',
        'CMAKE_INSTALL_BINDIR': 'bin',
    }

    def override_command(self, path):
        # point qtcreator settingspath to a custom location to make sure instance
        # share the same configuration
        # also add current project's dir to make qtcreator open directly the project
        p = ''
        if self.has_cmake_file() or self.has_qmake_file() or self.has_qbs_file():
            p = self.project_path
        else:
            logger.info('Unrecognized project, launch QtCreator without project preloaded')

        return path.replace('qtcreator', f'qtcreator -settingspath {Constants.clickable_dir} {p}')

    def before_run(self, config, docker_config):
        # if first qtcreator launch, install common settings
        if not os.path.isdir(self.target_settings_path):
            logger.info('copy initial qtcreator settings to %s', Constants.clickable_dir)
            tar = tarfile.open(self.init_settings_path)
            tar.extractall(Constants.clickable_dir)
            tar.close()

        if self.has_cmake_file() and not os.path.isfile(os.path.join(
            self.project_path,
            'CMakeLists.txt.user'
        )) and self.config.config['builder'] in [Constants.CMAKE, Constants.PURE_QML_CMAKE]:
            self.init_cmake_project(config, docker_config)

        # delete conflicting env vars in some cases
        docker_config.environment.pop("INSTALL_DIR", None)
        docker_config.environment.pop("APP_DIR", None)
        docker_config.environment.pop("SRC_DIR", None)

    def has_cmake_file(self):
        return os.path.isfile(os.path.join(self.project_path, 'CMakeLists.txt'))

    def has_qmake_file(self):
        for fname in os.listdir(self.project_path):
            if fname.endswith('.pro'):
                return True
        return False

    def has_qbs_file(self):
        for fname in os.listdir(self.project_path):
            if fname.endswith('.qbs'):
                return True
        return False

    # guess exec command and args from CMakeLists.txt
    # return None if nothing found
    def cmake_guess_exec_command(self, cmd_var):
        f = open(os.path.join(self.project_path, 'CMakeLists.txt'), 'r', encoding='UTF-8')
        cmake_file = f.read()
        output_cmd = None

        matches = self.pattern_cmake_vars.finditer(cmake_file)
        if matches:
            # store all cmake variable in a dictionnary
            cmake_vars = {}
            for k in matches:
                if k.group(1) not in cmake_vars:
                    value = k.group(2)
                    # strip quotes if any
                    if value.startswith('"'):
                        value = value[1:-1]
                    cmake_vars[k.group(1)] = value

            # try to find the exe command in cmake vars
            if cmd_var in cmake_vars:
                cmd = cmake_vars[cmd_var]
                # check if any vars in the exe command e.g "qmlscene ${MYVAR}"
                # and replace them by their value
                output_cmd = self.recurse_replace(cmd, cmake_vars)

        return output_cmd

    # replace recursively cmakeLists.txt variable by their values
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
                    cmd = cmd.replace('${' + var + '}', replacement)
                    cmd = self.recurse_replace(cmd, cmake_vars)
        return cmd

    # templates run/build generation for cmake project
    def init_cmake_project(self, config, docker_config):

        executable = config.project_files.find_any_executable()
        exec_args_list = config.project_files.find_any_exec_args()

        if exec_args_list:
            exec_args = " ".join(exec_args_list)
        else:
            exec_args = ""

        # don't do all that if exec line not found
        if not executable:
            return

        if not self.confirm('Do you want Clickable to setup a QtCreator project for you?'):
            return

        # CLICK_EXE can be a variable
        match_exe_var = re.match(r"@([-\w]+)@", executable)
        if match_exe_var:
            # catch the variable name and try to get it from CMakeLists.txt
            cmd_var = match_exe_var.group(1)
            final_cmd = self.cmake_guess_exec_command(cmd_var)
            if final_cmd is not None:
                try:
                    exe, exe_arg = final_cmd.split(' ', maxsplit=1)
                except ValueError:
                    exe, exe_arg = final_cmd, ''

                executable = exe
                exec_args = exe_arg
                logger.debug('found that executable is %s with args: %s', exe, exe_arg)
            else:
                # was not able to guess executable
                logger.warning(
                    "Could not determine executable command '%s', please adjust your run settings",
                    executable
                )

        # work around for qtcreator bug when first run of a project to avoid qtcreator hang
        # we need to create the build directory first
        if not os.path.isdir(config.build_dir):
            os.makedirs(config.build_dir)

        env_vars = docker_config.environment
        clickable_env_path = f'{env_vars["PATH"]}:{env_vars["CLICK_PATH"]}'
        clickable_ld_library_path = f'{env_vars["LD_LIBRARY_PATH"]}:' \
            f'{env_vars["CLICK_LD_LIBRARY_PATH"]}'
        lib_install_dir = os.path.join(config.install_dir, 'lib')
        clickable_qml2_import_path = f'{env_vars["QML2_IMPORT_PATH"]}:' \
            f'{env_vars["CLICK_QML2_IMPORT_PATH"]}:{lib_install_dir}'
        build_args = ''
        if config.build_args:
            build_args = ' '.join(self.config.build_args)
        clickable_build_args = f'{build_args} -DCMAKE_INSTALL_PREFIX:PATH=/.'

        template_replacement = {
            "CLICKABLE_LD_LIBRARY_PATH": clickable_ld_library_path,
            "CLICKABLE_QML2_IMPORT_PATH": clickable_qml2_import_path,
            "CLICKABLE_BUILD_DIR": config.build_dir,
            "CLICKABLE_INSTALL_DIR": config.install_dir,
            "CLICKABLE_EXEC_CMD": executable,
            "CLICKABLE_EXEC_ARGS": exec_args,
            "CLICKABLE_SRC_DIR": config.src_dir,
            "CLICKABLE_BUILD_ARGS": clickable_build_args,
            "CLICKABLE_PATH": clickable_env_path
        }

        output_path = os.path.join(self.project_path, 'CMakeLists.txt.user.shared')
        # now read template and generate the .shared file to the root project dir
        with open(self.template_path, 'r', encoding='UTF-8') as infile2, \
                open(output_path, 'w', encoding='UTF-8') as outfile:
            for line in infile2:
                for f_key, f_value in template_replacement.items():
                    if f_key in line:
                        line = line.replace(f_key, f_value)
                outfile.write(line)

        logger.info('generated default build/run template to %s', output_path)
