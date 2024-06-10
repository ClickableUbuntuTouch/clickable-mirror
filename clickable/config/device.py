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
            'default_target': 'ssh',
            'required': device_required,
            'always_detect': False,
            'xenial_adb': False,
        }

        if base:
            self.update(base)

        self.configure(args)

    @staticmethod
    def setup_parser(parser):
        command_group = parser.add_mutually_exclusive_group()
        command_group.add_argument(
            '--ssh',
            help='IPv4 address or hostname where device is reachable via SSH. '
            'Implies --target ssh.',
            default=None
        )
        command_group.add_argument(
            '--serial-number',
            '-s',
            help='Device or emulator with the given serial number or qualifier (using adb). '
            'Implies --target adb.',
            default=None
        )
        command_group.add_argument(
            '--target',
            '-t',
            choices=['ssh', 'adb', 'host', 'detect'],
            help='Target device. "detect" considers SSH first, then ADB, but never "host".',
        )

        parser.add_argument(
            '--xenial-adb',
            action='store_true',
            help='Use this when your target device is running Ubuntu 16.04 Xenial '
                 'and you are connected via ADB',
            default=False,
        )

    def parse_ssh_config(self, ssh_arg):
        result = re.match("(.+):([0-9]+)", ssh_arg)
        if result is not None:
            self.config['ipv4'] = result.group(1)
            self.config['ssh_port'] = result.group(2)
        else:
            self.config['ipv4'] = ssh_arg

    def configure(self, args=None):
        if env('CLICKABLE_DEFAULT_TARGET'):
            self.config['default_target'] = env('CLICKABLE_DEFAULT_TARGET')

        if env('CLICKABLE_SSH'):
            self.parse_ssh_config(env('CLICKABLE_SSH'))

        if env('CLICKABLE_SERIAL_NUMBER'):
            self.config['serial_number'] = env('CLICKABLE_SERIAL_NUMBER')

        if args:
            if args.xenial_adb:
                self.config['xenial_adb'] = True

            if args.target:
                self.config['selection'] = args.target

            if args.serial_number:
                if args.target and args.target != 'adb':
                    raise ClickableException(
                        f'--target {args.target} cannot be combined with --serial-number')

                self.config['serial_number'] = args.serial_number
                self.config['selection'] = 'adb'

            if args.ssh:
                if args.target and args.target != 'ssh':
                    raise ClickableException(
                        f'--target {args.target} cannot be combined with --ssh')

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
            'default_target': None,
            'always_detect': False,
        }

        self.update(config_file)
