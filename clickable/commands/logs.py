from clickable.logger import logger

from .base import Command


class LogsCommand(Command):
    def __init__(self):
        super().__init__()
        self.cli_conf.name = 'logs'
        self.cli_conf.help_msg = 'Follow the app\'s log file on the device'

    def run(self):
        if self.config.is_desktop_mode():
            logger.debug('Skipping logs, running in desktop mode')
            return

        if self.config.container_mode:
            logger.debug('Skipping logs, running in container mode')
            return

        log = '~/.cache/upstart/application-click-{}.log'.format(
            self.config.install_files.find_full_package_name(),
        )

        if self.config.log:
            log = self.config.log

        self.device.run_command('tail -f {}'.format(log))
