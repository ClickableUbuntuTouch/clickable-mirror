import atexit
import os
from subprocess import CalledProcessError

from clickable.logger import logger
from clickable.exceptions import ClickableException

from .base import Command


class GdbserverCommand(Command):
    def __init__(self):
        super().__init__()
        self.cli_conf.name = 'gdbserver'
        self.cli_conf.help_msg = 'Opens a gdbserver session on the device accessible ' \
            'at localhost:<port> (port 3333 by default)'
        self.command_conf.device_command = True
        self.command_conf.arch_specific = True

        self.port = 3333
        self.app_dir = None
        self.executable = None
        self.add_env = True
        self.desktop_file = None
        self.add_desktop_file_hint = True
        self.check_desktop_file = True
        self.hook_name = None

    def setup_parser(self, parser):
        parser.add_argument(
            '--port',
            default=self.port,
            help='Open local GDB Server specified port',
        )
        parser.add_argument(
            '--app-dir',
            help='Custom directory on the device where the gdbserver is started',
        )
        parser.add_argument(
            '--exec',
            help='Custom executable name',
        )
        parser.add_argument(
            '--no-app-env',
            action='store_true',
            help='Skip setting app environment',
        )
        parser.add_argument(
            '--desktop-file-hint',
            help='Custom desktop file to set desktop file hint',
        )
        parser.add_argument(
            '--no-desktop-file-hint',
            action='store_true',
            help='Custom desktop file to set desktop file hint',
        )
        parser.add_argument(
            '--no-desktop-file-check',
            action='store_true',
            help='Skip check for cached desktop file',
        )
        parser.add_argument(
            '--system-gdbserver',
            action='store_true',
            help='DEPRECATED: Use system gdbserver instead of pushing \
                    gdbserver to device home directory (this option has become \
                    superfluous, because Clickable will only push gdbserver if \
                    it is not yet available).',
        )
        parser.add_argument(
            '--hook',
            help='Debug the executable linked to a certain hook.',
        )

    def configure(self, args):
        self.port = args.port
        self.app_dir = args.app_dir
        self.executable = args.exec
        self.add_env = not args.no_app_env
        self.desktop_file = args.desktop_file_hint
        self.add_desktop_file_hint = not args.no_desktop_file_hint
        self.check_desktop_file = not args.no_desktop_file_check
        self.hook_name = args.hook

        if args.system_gdbserver:
            logger.warning("Deprecated option --system-gdbserver has been ignored.")

    def set_signal_handler(self):
        def cleanup():
            self.kill_gdbserver()
        atexit.register(cleanup)

    def get_app_dir(self):
        package_name = self.config.install_files.find_package_name()
        return f"/opt/click.ubuntu.com/{package_name}/current"

    def get_app_id(self):
        package_name = self.config.install_files.find_package_name()
        app_name = self.config.install_files.find_app_name()
        version = self.config.install_files.find_version()
        return f"{package_name}_{app_name}_{version}"

    def get_app_exec(self):
        desktop = self.config.install_files.get_desktop(
            self.config.install_dir,
            hook_name=self.hook_name
        )
        return desktop["Exec"]

    def get_app_exec_full_path(self):
        app_dir = self.get_app_dir()
        environ = self.get_app_env()
        app_exec = self.get_app_exec().split()

        commands = [f"cd {app_dir}",
                    f"PATH={environ['PATH']} which {app_exec[0]}"]
        output = self.device.run_command(commands, get_output=True).strip()
        path = output.splitlines()[-1]

        if app_exec[0] not in path:
            raise ClickableException("Could not find app executable in PATH on the device.")

        app_exec[0] = path
        return " ".join(app_exec)

    def get_app_env_xenial(self):
        package_name = self.config.install_files.find_package_name()
        app_name = self.config.install_files.find_app_name()
        app_id = self.get_app_id()

        environ = {
            "APP_DESKTOP_FILE_PATH": f"/opt/click.ubuntu.com/.click/users/phablet/{package_name}/{app_name}.desktop",  # noqa=E501
            "APP_DIR": f"/opt/click.ubuntu.com/.click/users/phablet/{package_name}",
            "APP_EXEC": self.get_app_exec(),
            "APP_ID": app_id,
            "__GL_SHADER_DISK_CACHE_PATH": f"/home/phablet/.cache/{package_name}",
            "TMPDIR": f"/run/user/32011/confined/{package_name}",
            "UPSTART_INSTANCE": app_id,
            "XDG_DATA_DIRS": f"/opt/click.ubuntu.com/.click/users/phablet/{package_name}:/usr/share/ubuntu-touch:/usr/share/ubuntu-touch:/usr/local/share/:/usr/share/:/custom/usr/share/",  # noqa=E501
            "LD_LIBRARY_PATH": f"/opt/click.ubuntu.com/.click/users/phablet/{package_name}/lib/{self.config.arch_triplet}:/opt/click.ubuntu.com/.click/users/phablet/{package_name}/lib",  # noqa=E501
            "PATH": f"/opt/click.ubuntu.com/.click/users/phablet/{package_name}/lib/{self.config.arch_triplet}/bin:/opt/click.ubuntu.com/.click/users/phablet/{package_name}:/home/phablet/bin:/home/phablet/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",  # noqa=E501
            "QML2_IMPORT_PATH": f"/usr/lib/{self.config.arch_triplet}/qt5/imports:/opt/click.ubuntu.com/.click/users/phablet/{package_name}/lib/{self.config.arch_triplet}",  # noqa=E501
            "UBUNTU_APP_LAUNCH_ARCH": self.config.arch_triplet,
            "APP_XMIR_ENABLE": "0",
            "DESKTOP_SESSION": "ubuntu-touch",
            "GDMSESSION": "ubuntu-touch",
            "GTK_IM_MODULE": "Maliit",
            "MIR_SERVER_HOST_SOCKET": "/run/mir_socket",
            "MIR_SERVER_NAME": "session-0",
            "MIR_SERVER_PROMPT_FILE": "1",
            "MIR_SOCKET": "/run/user/32011/mir_socket",
            "PULSE_CLIENTCONFIG": "/etc/pulse/touch-client.conf",
            "PULSE_PLAYBACK_CORK_STALLED": "1",
            "PULSE_PROP": "media.role=multimedia",
            "PULSE_SCRIPT": "/etc/pulse/touch.pa",
            "QML_NO_TOUCH_COMPRESSION": "1",
            "QT_ENABLE_GLYPH_CACHE_WORKAROUND": "1",
            "UBUNTU_APP_LAUNCH_XMIR_PATH": "/usr/bin/libertine-xmir",
            "UBUNTU_APPLICATION_ISOLATION": "1",
            "UPSTART_JOB": "application-click",
            "XDG_CACHE_HOME": "/home/phablet/.cache",
            "XDG_CONFIG_DIRS": "/etc/xdg/xdg-ubuntu-touch:/etc/xdg/xdg-ubuntu-touch:/etc/xdg",
            "XDG_CONFIG_HOME": "/home/phablet/.config",
            "XDG_CURRENT_DESKTOP": "Unity",
            "XDG_DATA_HOME": "/home/phablet/.local/share",
            "XDG_GREETER_DATA_DIR": "/var/lib/lightdm-data/phablet",
            "XDG_SEAT_PATH": "/org/freedesktop/DisplayManager/Seat0",
            "XDG_SEAT": "seat0",
            "XDG_SESSION_DESKTOP": "ubuntu-touch",
            "XDG_SESSION_PATH": "/org/freedesktop/DisplayManager/Session0",
            "XDG_SESSION_TYPE": "mir",
            "XDG_VTNR": "1",
        }

        return environ

    def get_app_env(self):
        if self.config.get_framework_base() == '16.04':
            return self.get_app_env_xenial()

        package_name = self.config.install_files.find_package_name()
        app_name = self.config.install_files.find_app_name()
        app_id = self.get_app_id()

        environ = {
            "APP_DESKTOP_FILE_PATH": f"/opt/click.ubuntu.com/.click/users/@all/{package_name}/{app_name}.desktop",  # noqa=E501
            "APP_DIR": f"/opt/click.ubuntu.com/.click/users/@all/{package_name}",
            "APP_ID": app_id,
            "APP_XMIR_ENABLE": "0",
            "DBUS_SESSION_BUS_ADDRESS": "unix:path=/run/user/32011/bus",
            "DESKTOP_FILE_HINT": "app_id",
            "DESKTOP_SESSION": "ubuntu-touch",
            "GDMSESSION": "ubuntu-touch",
            "GTK_IM_MODULE": "Maliit",
            "LD_LIBRARY_PATH": f"/opt/click.ubuntu.com/.click/users/@all/{package_name}/lib/{self.config.arch_triplet}:/opt/click.ubuntu.com/.click/users/@all/{package_name}/lib",  # noqa=E501
            "LD_PRELOAD": "libtls-padding.so",
            "LOMIRI_APPLICATION_ISOLATION": "1",
            "MIR_SERVER_ENABLE_MIRCLIENT": "1",
            "MIR_SERVER_ENABLE_X11": "1",
            "MIR_SERVER_FILE": "/run/user/32011/mir_socket",
            "MIR_SERVER_HOST_SOCKET": "/run/mir_socket",
            "MIR_SERVER_NAME": "session-0",
            "MIR_SERVER_XWAYLAND_PATH": "/usr/libexec/Xwayland.lomiri",
            "MIR_SOCKET": "/run/user/32011/mir_socket",
            "PATH": f"/opt/click.ubuntu.com/.click/users/@all/{package_name}/lib/{self.config.arch_triplet}/bin:/opt/click.ubuntu.com/.click/users/@all/{package_name}:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/snap/bin:/home/phablet/bin:/home/phablet/.local/bin",  # noqa=E501
            "PULSE_PROP": "media.role=multimedia",
            "QML2_IMPORT_PATH": f"/opt/click.ubuntu.com/.click/users/@all/{package_name}/lib/{self.config.arch_triplet}:/opt/click.ubuntu.com/.click/users/@all/{package_name}/lib/{self.config.arch_triplet}/qml",  # noqa=E501
            "QMLSCENE_DEVICE": "haliumqsgcontext",
            "QTWEBENGINE_CHROMIUM_FLAGS": "--enable-gpu-rasterization --enable-accelerated-video-decode --enable-features=MojoVideoDecoder",  # noqa=E501
            "QTWEBENGINE_DICTIONARIES_PATH": "/usr/share/hunspell-bdic/",
            "QTWEBKIT_DPR": "2.0",
            "QT_EXCLUDE_GENERIC_BEARER": "1",
            "QT_FILE_SELECTORS": "ubuntu-touch",
            "QT_IM_MODULE": "maliitphablet",
            "QT_QPA_PLATFORM": "ubuntumirclient",
            "QT_QUICK_CONTROLS_MOBILE": "1",
            "QT_QUICK_CONTROLS_STYLE": "Suru",
            "QV4_ENABLE_JIT_CACHE": "1",
            "SHELL": "/bin/bash",
            "SSH_AGENT_LAUNCHER": "gnome-keyring",
            "SSH_AUTH_SOCK": "/run/user/32011/keyring/ssh",
            "TMPDIR": f"/run/user/32011/confined/{package_name}",
            "WAYLAND_DISPLAY": "wayland-0",
            "XDG_CACHE_HOME": "/home/phablet/.cache",
            "XDG_CONFIG_DIRS": "/etc/xdg/xdg-ubuntu-touch:/etc/xdg",
            "XDG_CONFIG_HOME": "/home/phablet/.config",
            "XDG_CURRENT_DESKTOP": "Lomiri",
            "XDG_DATA_DIRS": f"/opt/click.ubuntu.com/.click/users/@all/{package_name}:/usr/share/ubuntu-touch:/usr/local/share:/usr/share:/custom/usr/share/",  # noqa=E501
            "XDG_DATA_HOME": "/home/phablet/.local/share",
            "XDG_GREETER_DATA_DIR": "/var/lib/lightdm-data/phablet",
            "XDG_RUNTIME_DIR": "/run/user/32011",
            "XDG_SEAT_PATH": "/org/freedesktop/DisplayManager/Seat0",
            "XDG_SESSION_CLASS": "user",
            "XDG_SESSION_DESKTOP": "ubuntu-touch",
            "XDG_SESSION_PATH": "/org/freedesktop/DisplayManager/Session0",
            "XDG_SESSION_TYPE": "mir",
            "ZEITGEIST_DATA_PATH": "/home/phablet/.local/share/zeitgeist",
            "__GL_SHADER_DISK_CACHE_PATH": f"/home/phablet/.cache/{package_name}",
        }

        return environ

    def get_cached_desktop_path(self):
        if self.config.get_framework_base() == '16.04':
            return os.path.join(
                "/home/phablet/.cache/ubuntu-app-launch/desktop",
                f"{self.get_app_id()}.desktop"
            )

        return os.path.join(
            "/home/phablet/.cache/lomiri-app-launch/desktop",
            f"{self.get_app_id()}.desktop"
        )

    def kill_gdbserver(self):
        processes = self.device.run_command(
            "ps aux | grep gdbserver",
            get_output=True
        )

        for line in processes.splitlines():
            if f"gdbserver localhost:{self.port}" in line:
                logger.debug("Killing running gdbserver on device")
                pid = line.split()[1]
                self.device.run_command(f"kill -9 {pid}")

    def check_cached_desktop_file(self):
        path = self.get_cached_desktop_path()
        try:
            self.device.run_command(
                f"ls {path} > /dev/null 2>&1",
                get_output=True
            ).strip()
        except Exception as err:
            raise ClickableException(
                'Failed to check installed version on device. The device is either '
                'not accessible or the app version you are trying to debug is not installed. '
                'Make sure the device is accessible or run "clickable install" and try again.'
            ) from err

    def push_gdbserver_to_device(self):
        self.container.setup()
        self.container.pull_files(["/usr/bin/gdbserver"], "/tmp/clickable")
        self.device.push_file('/tmp/clickable/gdbserver', '/home/phablet/bin/gdbserver')

    def is_gdbserver_available(self):
        try:
            self.device.run_command("which gdbserver", get_output=True)
            return True
        except CalledProcessError as e:
            if e.returncode == 1:
                return False
            raise e

    def start_gdbserver(self):
        if self.device.connection != "ssh":
            logger.warning(
                'SSH is recommended for the "gdbserver" command. If you experience '
                'any issues, try again with "--ssh"'
            )

        app_exec = self.executable
        desktop_file = self.desktop_file
        desktop_file_hint = ''
        app_dir = self.app_dir
        environ = {}

        if not self.executable:
            app_exec = self.get_app_exec_full_path()

        if not self.desktop_file:
            desktop_file = self.get_cached_desktop_path()

        if not app_dir:
            app_dir = self.get_app_dir()

        if self.add_env:
            environ = self.get_app_env()

        if self.add_desktop_file_hint:
            desktop_file_hint = f'--desktop_file_hint={desktop_file}'

        set_env = " ".join([f"{key}='{value}'" for key, value in environ.items()])
        commands = [
            f'cd {app_dir}',
            f'{set_env} gdbserver localhost:{self.port} {app_exec} {desktop_file_hint}',
        ]

        self.set_signal_handler()
        logger.debug(" ".join(commands))
        self.device.run_command(commands, forward_port=self.port)

    def run(self):
        if self.check_desktop_file:
            self.check_cached_desktop_file()

        if not self.is_gdbserver_available():
            self.push_gdbserver_to_device()

        self.start_gdbserver()
