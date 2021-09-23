from ..logger import logger


class BaseConfig():
    def __init__(self):
        self.config = {}

    def update(self, config_file):
        valid_config = {k: v for k, v in config_file.items() if k in self.config}
        self.config.update(valid_config)

        remaining_keys = [k for k in config_file if k not in self.config]
        for k in remaining_keys:
            logger.debug('Ignored unknown config key "%s"', k)

    def __getattr__(self, name):
        return self.config[name]
