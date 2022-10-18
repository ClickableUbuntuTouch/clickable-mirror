from clickable.config.constants import Constants
from clickable.config.project import ProjectConfig
from clickable.commands.docker.docker_config import DockerConfig
from clickable.utils import get_existing_dir
from .docker_support import DockerSupport
import os


class MultimediaSupport(DockerSupport):
    config = None

    def __init__(self, config: ProjectConfig):
        self.config = config

    def update(self, docker_config: DockerConfig):
        uid = os.getuid()

        pulse_run_dir = get_existing_dir('Pulse run', [
            f'/run/user/{uid}/pulse',
            f'/run/{uid}/pulse',
        ], optional=True)

        pulse_conf_dir = get_existing_dir('Pulse configuration', [
            os.path.join(Constants.host_home, '.pulse'),
            os.path.join(Constants.host_home, '.config/pulse'),
        ], optional=True)

        docker_config.volumes.update({
            '/dev/shm': '/dev/shm',
            '/etc/machine-id': '/etc/machine-id',
            '/var/lib/dbus': '/var/lib/dbus',
            '/dev/snd': '/dev/snd',
        })

        if pulse_run_dir:
            docker_config.volumes[pulse_run_dir] = '/run/user/1000/pulse'

        if pulse_conf_dir:
            docker_config.volumes[pulse_conf_dir] = os.path.join(Constants.device_home, '.pulse')
