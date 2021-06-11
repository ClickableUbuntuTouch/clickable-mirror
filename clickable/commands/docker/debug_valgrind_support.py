from clickable.commands.docker.docker_config import DockerConfig
from .docker_support import DockerSupport


class DebugValgrindSupport(DockerSupport):
    def update(self, docker_config: DockerConfig):
        docker_config.execute = 'valgrind {}'.format(docker_config.execute)
