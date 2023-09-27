import os

from clickable.config.constants import Constants
from clickable.logger import logger

from .base import Command


class InstallCommand(Command):
    def __init__(self):
        super().__init__()
        self.cli_conf.name = 'install'
        self.cli_conf.help_msg = 'Takes a built click package and installs it on a device'
        self.command_conf.device_command = True
        self.command_conf.arch_specific = True

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
            if self.config.get_framework_base() == '16.04':
                logger.debug("Using UT 16.04 uninstall command")
                command = ['pkcon', 'remove', f'\\"{package_name};{version};all;local:click\\"']
            else:
                logger.debug("Using UT 20.04 uninstall command")
                command = [
                    'gdbus',
                    'call',
                    '--system',
                    '--dest com.lomiri.click',
                    '--object-path /com/lomiri/click',
                    '--method com.lomiri.click.Remove',
                    package_name]

            logger.info("Trying to uninstall the app first.")
            command = ' '.join(command)
            self.device.run_command(command)

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

        dst_path = os.path.join(Constants.device_home, click)
        self.device.push_file(self.click_path, dst_path)

        if self.skip_uninstall:
            logger.info("Skipping uninstall pre-step.")
        else:
            self.try_uninstall()

        logger.info("Installing the app.")

        if self.config.get_framework_base() == '16.04':
            logger.debug("Using UT 16.04 install command")
            command = ['pkcon', 'install-local', '--allow-untrusted', f'/home/phablet/{click}']
        else:
            logger.debug("Using UT 20.04 install command")
            command = [
                'gdbus',
                'call',
                '--system',
                '--dest com.lomiri.click',
                '--object-path /com/lomiri/click',
                '--method com.lomiri.click.Install',
                f'/home/phablet/{click}']

        command = ' '.join(command)
        self.device.run_command(command, cwd=cwd)

        logger.info("Cleaning up.")
        self.device.run_command(f'rm {dst_path}', cwd=cwd)
