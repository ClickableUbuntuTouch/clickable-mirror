import re

from clickable.exceptions import ClickableException
from clickable.logger import logger
from clickable.utils import env

from .base import BaseConfig


class DeviceConfig(BaseConfig):
    def __init__(self, base=None, args=None, device_required=False):
        super().__init__()
        self.config = {
            'ipv4': None,
            'ssh_port': None,
            'serial_number': None,
            'skip_uninstall': False,
            'selection': 'detect',
            'default_device': 'ssh',
            'required': device_required,
            'always_detect': False,
        }

        if base:
            self.update(base)

        self.configure(args)

    @staticmethod
    def setup_parser(parser):
        command_group = parser.add_mutually_exclusive_group()
        command_group.add_argument(
            '--ssh',
            help='IPv4 address where device is reachable via SSH. '
            'Disables device detection.',
            default=None
        )
        command_group.add_argument(
            '--serial-number',
            '-s',
            help='Device or emulator with the given serial number or qualifier (using adb). '
            'Disables device detection.',
            default=None
        )
        command_group.add_argument(
            '--device',
            '-d',
            choices=['ssh', 'adb', 'host', 'detect'],
            help='Target device. "detect" considers SSH first, then ADB, but never "host".',
        )

    def parse_ssh_config(self, ssh_arg):
        result = re.match("(.+):([0-9]+)", ssh_arg)
        if result is not None:
            self.config['ipv4'] = result.group(1)
            self.config['ssh_port'] = result.group(2)
        else:
            self.config['ipv4'] = ssh_arg

    def configure(self, args=None):
        if env('CLICKABLE_DEFAULT_DEVICE'):
            self.config['default_device'] = env('CLICKABLE_DEFAULT_DEVICE')

        if env('CLICKABLE_SSH'):
            self.parse_ssh_config(env('CLICKABLE_SSH'))

        if env('CLICKABLE_SERIAL_NUMBER'):
            self.config['serial_number'] = env('CLICKABLE_SERIAL_NUMBER')

        if args:
            if args.device:
                self.config['selection'] = args.device

            if args.serial_number:
                self.config['serial_number'] = args.serial_number
                self.config['selection'] = 'abd'

            if args.ssh:
                self.parse_ssh_config(args.ssh)
                self.config['selection'] = 'ssh'

        if self.config['selection'] == 'ssh' and not self.config['ipv4']:
            raise ClickableException("Cannot use SSH without an IP address specified")

        if self.config['always_detect']:
            self.config['required'] = True


class GlobalDeviceConfig(BaseConfig):
    def __init__(self, config_file):
        super().__init__()

        if 'arch' in config_file:
            logger.warning('Ignoring deprecated "arch" in "device" config section. '
                           'Specify "default_arch" in "build" section instead.')
            del config_file['arch']

        self.config = {
            'ipv4': None,
            'ssh_port': None,
            'serial_number': None,
            'skip_uninstall': False,
            'default_device': None,
            'always_detect': False,
        }

        self.update(config_file)
