from .base import BaseConfig


class DeviceConfig(BaseConfig):
    def __init__(self, config_file):
        super().__init__()

        self.config = {
            'ipv4': None,
            'ssh_port': None,
            'serial_number': None,
            'arch': None,
            'skip_uninstall': False,
        }

        self.update(config_file)
