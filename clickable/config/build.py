from .base import BaseConfig


class BuildConfig(BaseConfig):
    def __init__(self, config_file):
        super().__init__()

        self.config = {
            'always_clean': False,
            'skip_review': False,
            'default_arch': None,
        }

        self.update(config_file)
