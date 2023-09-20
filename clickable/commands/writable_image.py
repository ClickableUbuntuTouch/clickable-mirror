from clickable.logger import logger

from .base import Command


class WritableImageCommand(Command):
    def __init__(self):
        super().__init__()
        self.cli_conf.name = 'writable-image'
        self.cli_conf.help_msg = 'Make your Ubuntu Touch device\'s rootfs writable'
        self.command_conf.device_command = True

    def run(self):
        command = 'dbus-send --system --print-reply --dest=com.canonical.PropertyService ' \
                  '/com/canonical/PropertyService com.canonical.PropertyService.SetProperty ' \
                  'string:writable boolean:true'
        self.device.run_command(command, cwd=self.config.cwd)
        logger.info('Rebooting device for writable image')
