from .base import Command
from clickable.logger import logger


class DevicesCommand(Command):
    def __init__(self):
        super().__init__()
        self.cli_conf.name = 'devices'
        self.cli_conf.help_msg = 'Lists all connected devices'

    def run(self):
        devices = self.device.detect_attached()

        if len(devices) == 0:
            logger.warning('No attached devices')
        else:
            for device in devices:
                logger.info(device)
