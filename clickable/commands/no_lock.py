from clickable.logger import logger

from .base import Command


class NoLockCommand(Command):
    def __init__(self):
        super().__init__()
        self.cli_conf.name = 'no-lock'
        self.cli_conf.help_msg = "Turns off the device's display timeout"
        self.command_conf.device_command = True

    def run(self):
        logger.info('Turning off device activity timeout')
        if self.config.get_framework_base() == '16.04':
            command = 'gsettings set com.ubuntu.touch.system activity-timeout 0'
        else:
            command = 'gsettings set com.lomiri.touch.system activity-timeout 0'
        self.device.run_command(command, cwd=self.config.cwd)
