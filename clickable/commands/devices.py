from clickable.logger import logger

from .base import Command


class DevicesCommand(Command):
    def __init__(self):
        super().__init__()
        self.cli_conf.name = 'devices'
        self.cli_conf.help_msg = 'Lists all ADB devices'

    def run(self):
        devices = self.device.detect_adb_attached()

        if len(devices) == 0:
            logger.warning('No attached devices')
        else:
            for device in devices:
                logger.info(device)
