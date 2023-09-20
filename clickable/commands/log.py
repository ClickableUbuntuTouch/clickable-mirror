from clickable.logger import logger

from .base import Command


class LogCommand(Command):
    def __init__(self):
        super().__init__()
        self.cli_conf.name = 'log'
        self.cli_conf.help_msg = 'Outputs the existing app\'s log from the device'
        self.command_conf.device_command = True

    def run(self):
        if self.config.is_desktop_mode():
            logger.debug('Skipping log, running in desktop mode')
            return

        if self.config.container_mode:
            logger.debug('Skipping log, running in container mode')
            return

        package_name = self.config.install_files.find_full_package_name()
        if self.config.get_framework_base() == '16.04':
            logger.debug("Using UT 16.04 log command")

            log = f'~/.cache/upstart/application-click-{package_name}.log'
            self.device.run_command(f'cat {log}')
        else:
            logger.debug("Using UT 20.04 log command")

            print(self.device.run_command(
                'journalctl --user --no-pager -u '
                f'lomiri-app-launch--application-click--{package_name}--',
                get_output=True
            ))
