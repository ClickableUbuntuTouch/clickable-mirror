from .base import BaseConfig


class IdeConfig(BaseConfig):
    def __init__(self, config_file):
        super().__init__()

        self.config = {
            'default': 'qtcreator',
            'image_setup': {},
        }

        self.update(config_file)
