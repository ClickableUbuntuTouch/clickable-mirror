from .base import BaseConfig


class BuildConfig(BaseConfig):
    def __init__(self, config_file):
        super().__init__()

        self.config = {
            'always_clean': False,
            'skip_review': False,
        }

        self.update(config_file)
