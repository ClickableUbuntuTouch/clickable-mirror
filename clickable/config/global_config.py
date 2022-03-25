import os
import yaml

from clickable.exceptions import ClickableException

from clickable.utils import (
    load_config_schema,
    validate_config_format,
)

from .device import GlobalDeviceConfig
from .build import BuildConfig
from .environment import EnvironmentConfig
from .cli import CliConfig
from .ide import IdeConfig

from .constants import Constants


class GlobalConfig():
    def __init__(self, custom_path):
        path = custom_path if custom_path else Constants.clickable_config_path
        config = self.load(path, custom_path)
        schema = load_config_schema('clickable')
        validate_config_format(config, schema, 'Clickable', path)

        self.device = GlobalDeviceConfig(config.get('device', {}))
        self.build = BuildConfig(config.get('build', {}))
        self.environment = EnvironmentConfig(config.get('environment', {}))
        self.cli = CliConfig(config.get('cli', {}))
        self.ide = IdeConfig(config.get('ide', {}))

    def load(self, path, is_custom):
        if not os.path.exists(path):
            if is_custom:
                raise ClickableException(
                    f'Specified Clickable config file "{path}" does not exist.'
                )
            return {}

        with open(path, 'r', encoding='UTF-8') as f:
            try:
                return yaml.safe_load(f)
            except ValueError as err:
                raise ClickableException(
                    f'Failed reading Clickable config from "{path}". It is not valid yaml file.'
                ) from err
