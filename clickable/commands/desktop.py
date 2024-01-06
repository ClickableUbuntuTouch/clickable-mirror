import os
import shlex
import subprocess
from pathlib import Path
import re
import shutil
import filecmp

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    HAS_WATCHDOG = True
except ImportError:
    HAS_WATCHDOG = False

from clickable.utils import (
    find_pattern,
    is_command,
    makedirs,
    pull_image,
    run_subprocess_check_output,
    env,
)
from clickable.config.constants import Constants
from clickable.logger import logger
from clickable.exceptions import ClickableException

from .base import Command
from .build import BuildCommand
from .docker.debug_gdb_support import DebugGdbSupport
from .docker.debug_valgrind_support import DebugValgrindSupport
from .docker.docker_config import DockerConfig
from .docker.go_support import GoSupport
from .docker.nvidia_support import NvidiaSupport
from .docker.rust_support import RustSupport
from .docker.webapp_support import WebappSupport
from .docker.theme_support import ThemeSupport
from .docker.multimedia_support import MultimediaSupport


class DesktopCommand(Command):
    def __init__(self):
        super().__init__()
        self.cli_conf.name = 'desktop'
        self.cli_conf.help_msg = 'Run the app on your desktop'

        self.command = None
        self.custom_mode = False
        self.ide_delegate = None
        self.skip_build = False
        self.gdb_port = None
        self.gdb = False
        self.valgrind = False
        self.dark_mode = False
        self.desktop_locale = 'C'
        self.qmllive = False
        self.file_observer = None

        self.builder = BuildCommand(skip_review=True, skip_click=True)

    def setup_parser(self, parser):
        self.builder.setup_parser(parser)

        parser.add_argument(
            '--skip-build',
            action='store_true',
            help='Start app without building it first',
            default=False,
        )
        parser.add_argument(
            '--gdbserver',
            help='Start gdbserver at the given port to debug the app remotely via any IDE',
        )
        parser.add_argument(
            '--gdb',
            action='store_true',
            help='Start gdb to debug the app',
            default=False,
        )
        parser.add_argument(
            '--valgrind',
            action='store_true',
            help='Start valgrind to debug the app',
            default=False,
        )
        parser.add_argument(
            '--qmllive',
            action='store_true',
            help='Enable live update of qml files. \
                    Only works for apps that are started via "qmlscene".',
            default=False,
        )
        parser.add_argument(
            '--dark-mode',
            action='store_true',
            help='Use the dark theme when running apps',
            default=False,
        )
        parser.add_argument(
            '--lang',
            help='Start app with the given language code',
            default=os.getenv('LANG', 'C')
        )

    def configure(self, args):
        self.builder.init_from_command(self)
        self.builder.configure(args)

        self.skip_build = args.skip_build
        self.gdb_port = args.gdbserver
        self.gdb = args.gdb or self.gdb_port
        self.valgrind = args.valgrind
        self.qmllive = args.qmllive
        self.dark_mode = args.dark_mode
        self.desktop_locale = args.lang

        if self.qmllive and self.skip_build:
            logger.warning(
                'Combining --skip-build and --qmllive is dangerous, \
                        because QML files in source and install dir need to be identical \
                        at start for the live update to work.')

        self.configure_common()

    def configure_nested(self):
        self.builder.init_from_command(self)
        self.configure_common()

    def configure_common(self):
        if env('CLICKABLE_DARK_MODE'):
            self.dark_mode = True

        if self.gdb or self.valgrind:
            self.builder.debug_build = True

        if self.valgrind and self.gdb:
            raise ClickableException(
                "Valgrind (--valgrind) and GDB (--gdb or --gdbserver) can not be combined."
            )

        if self.desktop_locale != "C" and "." not in self.desktop_locale:
            self.desktop_locale = f"{self.desktop_locale}.UTF-8"

    def run(self):
        if self.container.docker_desktop:
            raise ClickableException("Desktop Mode isn't supported when using Docker Desktop.")

        self.prepare_run()
        self.run_app()

    def prepare_run(self):
        if self.skip_build or self.custom_mode:
            self.container.setup()
        else:
            self.builder.run()

    def setup_docker(self):
        self.container.check_docker()
        if is_command('xhost'):
            subprocess.check_call(shlex.split('xhost +local:docker'))
        else:
            logger.warning('xhost not installed, desktop mode may fail')

        return self.setup_docker_config()

    def setup_docker_config(self):
        docker_config = DockerConfig()

        docker_config.uid = os.getuid()
        docker_config.docker_image = self.container.docker_image
        docker_config.use_nvidia = self.config.use_nvidia

        if self.custom_mode:
            docker_config.execute = self.command
            docker_config.working_directory = self.config.root_dir
            docker_config.pseudo_tty = True

            executable = self.config.project_files.find_any_executable()
            exec_args = self.config.project_files.find_any_exec_args()
            if executable:
                docker_config.add_environment_variables(
                    {
                        "CLICK_EXEC": executable,
                        "CLICK_EXEC_PARAMS": " ".join(exec_args),
                    })
        else:
            docker_config.pseudo_tty = self.gdb
            docker_config.execute = self.determine_executable(
                self.find_desktop_file()
            )
            docker_config.working_directory = self.config.install_dir

            WebappSupport(self.config.install_files.find_package_name()).update(docker_config)
            ThemeSupport(self.config, self.dark_mode).update(docker_config)

            if self.gdb:
                DebugGdbSupport(self.gdb_port).update(docker_config)
            if self.valgrind:
                DebugValgrindSupport().update(docker_config)

        docker_config.add_environment_variables(
            {
                "CLICKABLE_DESKTOP_MODE": "1",
            })

        docker_config.add_volume_mappings(self.setup_volume_mappings())

        docker_config.add_environment_variables(
            self.setup_environment(docker_config.working_directory)
        )

        NvidiaSupport().update(docker_config)
        MultimediaSupport(self.config).update(docker_config)

        GoSupport(self.config).update(docker_config)
        RustSupport(self.config).update(docker_config)

        return docker_config

    def find_desktop_file(self):
        desktop_path = None
        hooks = self.config.install_files.get_manifest().get('hooks', {})
        try:
            app = self.config.install_files.find_app_name()
            if app in hooks and 'desktop' in hooks[app]:
                desktop_path = hooks[app]['desktop']
        except ClickableException:
            for _, value in hooks.items():
                if 'desktop' in value:
                    desktop_path = value['desktop']
                    break

        if not desktop_path:
            raise ClickableException('Could not find desktop file for app')

        desktop_path = os.path.join(self.config.install_dir, desktop_path)
        if not os.path.exists(desktop_path):
            raise ClickableException(
                f'Could not determine executable. Desktop file does not exist: "{desktop_path}"'
            )

        return desktop_path

    def determine_executable(self, desktop_path):
        execute = None
        with open(desktop_path, 'r', encoding='UTF-8') as desktop_file:
            for line in desktop_file.readlines():
                if line.startswith('Exec='):
                    execute = line
                    break

        if not execute:
            raise ClickableException(f'No "Exec" line found in the desktop file {desktop_path}')

        execute = re.sub(' %\\w', '', execute)
        return execute[len('Exec='):].strip()

    def get_time_zone(self):
        try:
            return run_subprocess_check_output(
                'timedatectl show -p Timezone --value',
                stderr=subprocess.DEVNULL).strip()
        except Exception:  # pylint: disable=broad-except
            logger.debug(
                'timedatectl show command failed. Falling back to alternative way '
                'to detect timezone...'
            )

        if os.path.exists('/etc/timezone'):
            with open('/etc/timezone', 'r', encoding='UTF-8') as host_timezone_file:
                return host_timezone_file.readline().strip()
        else:
            logger.debug(
                '/etc/timezone does not exist. Falling back to alternative way '
                'to detect timezone...'
            )

        try:
            output = run_subprocess_check_output('timedatectl status')
            for line in output.splitlines():
                line = line.strip()
                if line.startswith('Time zone:'):
                    start = line.find(':') + 1
                    end = line.find('(')
                    return line[start:end].strip()
        except Exception:  # pylint: disable=broad-except
            logger.debug(
                "timedatctl status method failed to set timezone from host in desktop mode..."
            )

        logger.debug("Falling back to UTC as timezone.")
        return 'UTC'

    def setup_environment(self, working_directory):
        lib_path = self.get_docker_lib_path_env(working_directory)

        env_vars = {
            'LANG': self.desktop_locale,
            'LANGUAGE': self.desktop_locale,
            'LC_CTYPE': self.desktop_locale,
            'LC_NUMERIC': self.desktop_locale,
            'LC_TIME': self.desktop_locale,
            'LC_COLLATE': self.desktop_locale,
            'LC_MONETARY': self.desktop_locale,
            'LC_MESSAGES': self.desktop_locale,
            'LC_PAPER': self.desktop_locale,
            'LC_NAME': self.desktop_locale,
            'LC_ADDRESS': self.desktop_locale,
            'LC_TELEPHONE': self.desktop_locale,
            'LC_MEASUREMENT': self.desktop_locale,
            'LC_IDENTIFICATION': self.desktop_locale,
            'LC_ALL': self.desktop_locale,
            'TZ': self.get_time_zone(),
            'APP_DIR': self.config.install_dir,
            'TEXTDOMAINDIR': self.config.install_files.try_find_locale(),
            'XAUTHORITY': '/tmp/.docker.xauth',
            'DISPLAY': os.environ['DISPLAY'],
            'QML2_IMPORT_PATH': lib_path,
            'LD_LIBRARY_PATH': lib_path,
            'PATH': self.get_docker_path_env(working_directory) + self.get_image_path_var(),
            'HOME': Constants.device_home,
            'OXIDE_NO_SANDBOX': '1',
            'UBUNTU_APP_LAUNCH_ARCH': self.config.arch_triplet,
            'UITK_ICON_THEME': 'suru',
        }

        if self.custom_mode:
            env_vars.update(self.config.get_env_vars())
            env_vars['HOME'] = os.environ['HOME']

        return env_vars

    def get_docker_lib_path_env(self, working_directory):
        return ':'.join([
            os.path.join(working_directory, f'lib/{self.config.arch_triplet}'),
            os.path.join(working_directory, 'lib'),
            '/usr/local/nvidia/lib',
            '/usr/local/nvidia/lib64',
        ])

    def get_docker_path_env(self, working_directory):
        return ':'.join([
            self.config.app_bin_dir,
            working_directory,
            '/usr/local/nvidia/bin',
            '/bin',
            '/usr/bin',
        ])

    def get_image_path_var(self):
        pull_image(self.config.docker_image)

        command = f"{self.container.docker_executable} inspect -f "\
            "'{{range $index, $value := .Config.Env}}{{println $value}}{{end}}' " \
            f"{self.config.docker_image}"
        image_env = run_subprocess_check_output(command).splitlines()
        for var in image_env:
            if var.startswith("PATH="):
                return ":" + var.rsplit("=", 1)[1]

        return ""

    def setup_volume_mappings(self):
        xauth_path = self.touch_xauth()

        device_home = Constants.desktop_device_home
        makedirs(device_home)
        logger.info("Mounting device home to %s", device_home)

        vol_map = {
            self.config.cwd: self.config.cwd,
            '/tmp/.X11-unix': '/tmp/.X11-unix',
            xauth_path: xauth_path,
            device_home: '/home/phablet',
            '/etc/passwd': '/etc/passwd',
        }

        if self.custom_mode:
            vol_map[Constants.host_home] = Constants.host_home

        return vol_map

    def touch_xauth(self):
        xauth_path = '/tmp/.docker.xauth'
        Path(xauth_path).touch()
        return xauth_path

    def run_app(self):
        docker_config = self.setup_docker()

        if self.ide_delegate is not None:
            self.ide_delegate.before_run(self.config, docker_config)

        if self.qmllive:
            if 'qmlscene' not in docker_config.execute:
                raise ClickableException(
                    '--qmllive can only be used on apps that start via qmlscene \
                            (see your desktop file)')

            docker_config.execute = docker_config.execute.replace('qmlscene', 'qmllive')
            self.run_qmllive_observer()

        id_mapping_string = self.container.render_id_mapping_string()
        command = docker_config.render_command(self.container.docker_executable, id_mapping_string)
        logger.debug(command)

        subprocess.check_call(shlex.split(command), cwd=docker_config.working_directory)

        if self.qmllive:
            self.file_observer.stop()

    def run_qmllive_observer(self):
        if not HAS_WATCHDOG:
            raise ClickableException('The qmllive feature requres the python module "watchdog" \
                    which is not installed')

        qml_src_files = find_pattern(
            "**/*.qml",
            self.config.src_dir,
            exclude_dir=self.config.install_dir)
        qml_install_files = find_pattern("**/*.qml", self.config.install_dir)
        file_map = {}

        for install_file in qml_install_files:
            for src_file in qml_src_files:
                if filecmp.cmp(src_file, install_file):
                    file_map[os.path.normpath(src_file)] = install_file

        if not qml_install_files:
            logger.warning('No QML files found for QML live update.')
        elif not file_map:
            logger.warning(
                'No QML files could be matched between src dir and install dir \
                        for QML live update.')

        class Handler(FileSystemEventHandler):
            def __init__(self, file_map):
                super().__init__()
                self.file_map = file_map

            def on_modified(self, event):
                src = os.path.normpath(event.src_path)
                dst = self.file_map.get(src, None)

                if dst and not filecmp.cmp(src, dst):
                    shutil.copy(src, dst)

        self.file_observer = Observer()
        self.file_observer.schedule(Handler(file_map), self.config.src_dir, recursive=True)
        self.file_observer.start()
