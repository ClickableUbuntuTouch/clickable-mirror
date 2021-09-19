import os

from clickable.utils import run_subprocess_check_call
from clickable.logger import logger

from .base import Command


class InstallCommand(Command):
    def __init__(self):
        super().__init__()
        self.cli_conf.name = 'install'
        self.cli_conf.help_msg = 'Takes a built click package and installs it on a device'

        self.click_path = None
        self.skip_uninstall = False

    def setup_parser(self, parser):
        parser.add_argument(
            'click',
            nargs='?',
            help='Click package to be installed (defaults to the one created by Clickable)'
        )
        parser.add_argument(
            '--skip-uninstall',
            action='store_true',
            help='Skip uninstall pre-step which ensures that new AppArmor permissions '
                 'are applied even without a version number change'
        )

    def configure(self, args):
        self.click_path = args.click
        self.skip_uninstall = args.skip_uninstall or self.click_path

    def configure_nested(self):
        self.configure_common()

    def configure_common(self):
        if self.config.global_config.device.skip_uninstall:
            self.skip_uninstall = True

    def try_find_installed_version(self, package_name):
        try:
            response = self.device.run_command(
                f'readlink /opt/click.ubuntu.com/{package_name}/current',
                get_output=True
            )
            return response.splitlines()[-1]
        except Exception:  # pylint: disable=broad-except
            return None

    def try_uninstall(self):
        package_name = self.config.install_files.find_package_name()
        version = self.try_find_installed_version(package_name)

        if version:
            logger.info("Uninstalling the app first.")
            self.device.run_command(
                f'pkcon remove \\"{package_name};{version};all;local:click\\"'
            )

    def run(self):
        if self.config.is_desktop_mode():
            logger.debug('Skipping install, running in desktop mode')
            return

        if self.config.container_mode:
            logger.debug('Skipping install, running in container mode')
            return

        cwd = '.'
        if self.click_path:
            click = os.path.basename(self.click_path)
        else:
            click = self.config.install_files.get_click_filename()
            self.click_path = os.path.join(self.config.build_dir, click)
            cwd = self.config.build_dir

        if self.config.ssh:
            command = f'scp {self.click_path} phablet@{self.config.ssh}:/home/phablet/'
            run_subprocess_check_call(command, cwd=cwd, shell=True)

        else:
            self.device.check_any_adb_attached()

            if self.config.device_serial_number:
                command = f'adb -s {self.config.device_serial_number} push {self.click_path} ' \
                          '/home/phablet/'
            else:
                self.device.check_multiple_adb_attached()
                command = f'adb push {self.click_path} /home/phablet/'

            run_subprocess_check_call(command, cwd=cwd, shell=True)

        if self.skip_uninstall:
            logger.info("Skipping uninstall pre-step.")
        else:
            self.try_uninstall()

        logger.info("Installing the app.")
        self.device.run_command(
            f'pkcon install-local --allow-untrusted /home/phablet/{click}',
            cwd=cwd
        )
        logger.info("Cleaning up.")
        self.device.run_command(f'rm /home/phablet/{click}', cwd=cwd)
