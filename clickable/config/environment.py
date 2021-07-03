from .base import BaseConfig


class EnvironmentConfig(BaseConfig):
    def __init__(self, config_file):
        super().__init__()

        self.config = {
            'non_interactive': False,
            'container_mode': False,
            'restrict_arch': None,
            'nvidia': 'auto',
        }

        self.update(config_file)
