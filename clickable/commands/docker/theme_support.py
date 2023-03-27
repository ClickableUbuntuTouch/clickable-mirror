import os

from clickable.commands.docker.docker_config import DockerConfig
from clickable.utils import makedirs
from clickable.config.constants import Constants
from .docker_support import DockerSupport


class ThemeSupport(DockerSupport):
    def __init__(self, config, dark_mode):
        self.config = config
        self.dark_mode = dark_mode

    def update(self, docker_config: DockerConfig):
        if self.config.get_framework_base() == '16.04':
            folder = "ubuntu-ui-toolkit"
            theme_base = 'Ubuntu.Components.Themes'
        else:
            folder = "lomiri-ui-toolkit"
            theme_base = 'Lomiri.Components.Themes'

        if self.dark_mode:
            theme_name = 'SuruDark'
        else:
            theme_name = 'Ambiance'

        config_dir = os.path.join(
            Constants.desktop_device_home,
            '.config',
            folder,
        )

        makedirs(config_dir)
        with open(os.path.join(config_dir, 'theme.ini'), 'w') as f:
            f.write(f'[General]\ntheme={theme_base}.{theme_name}')
