from clickable.logger import logger

from .base import Command


class LogCommand(Command):
    def __init__(self):
        super().__init__()
        self.cli_conf.name = 'log'
        self.cli_conf.help_msg = 'Outputs the existing app\'s log from the device'

    def run(self):
        if self.config.is_desktop_mode():
            logger.debug('Skipping log, running in desktop mode')
            return

        if self.config.container_mode:
            logger.debug('Skipping log, running in container mode')
            return

        package_name = self.config.install_files.find_full_package_name()
        log = f'~/.cache/upstart/application-click-{package_name}.log'

        if self.config.log:
            log = self.config.log

        self.device.run_command(f'cat {log}')
