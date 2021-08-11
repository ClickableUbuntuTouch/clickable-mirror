from clickable.logger import logger

from .base import Command


class NoLockCommand(Command):
    def __init__(self):
        super().__init__()
        self.cli_conf.name = 'no-lock'
        self.cli_conf.help_msg = "Turns off the device's display timeout"

    def run(self):
        logger.info('Turning off device activity timeout')
        command = 'gsettings set com.ubuntu.touch.system activity-timeout 0'
        self.device.run_command(command, cwd=self.config.cwd)
