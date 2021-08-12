from .base import BaseConfig


class CliConfig(BaseConfig):
    def __init__(self, config_file):
        super().__init__()

        self.config = {
            'default_chain': 'build install launch',
            'scripts': {},
        }

        self.update(config_file)
