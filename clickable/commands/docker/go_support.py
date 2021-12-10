import os

from clickable.config.project import ProjectConfig
from clickable.config.constants import Constants
from clickable.commands.docker.docker_config import DockerConfig
from .docker_support import DockerSupport


class GoSupport(DockerSupport):
    config = None

    def __init__(self, config: ProjectConfig):
        self.config = config

    def update(self, docker_config: DockerConfig):
        if self.config.builder == Constants.GO and self.config.gopath:
            gopaths = self.config.gopath.split(':')
            for (index, path) in enumerate(gopaths):
                os.makedirs(path, exist_ok=True)

                docker_config.add_volume_mappings({
                    path: f'/gopath/path{index}'
                })

            docker_config.add_environment_variables({
                'GOPATH': self.config.gopath
            })
