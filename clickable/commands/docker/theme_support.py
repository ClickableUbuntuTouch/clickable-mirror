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
        config_path = makedirs(os.path.join(
            Constants.desktop_device_home,
            '.config/ubuntu-ui-toolkit'
        ))

        theme = 'Ubuntu.Components.Themes.Ambiance'
        if self.dark_mode:
            theme = 'Ubuntu.Components.Themes.SuruDark'

        with open(os.path.join(config_path, 'theme.ini'), 'w') as f:
            f.write('[General]\ntheme=' + theme)
