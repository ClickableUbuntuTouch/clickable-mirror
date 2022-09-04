from clickable.config.project import ProjectConfig
from clickable.commands.docker.docker_config import DockerConfig
from clickable.utils import get_existing_dir
from .docker_support import DockerSupport
import os
import getpass


class MultimediaSupport(DockerSupport):
    config = None

    def __init__(self, config: ProjectConfig):
        self.config = config

    def update(self, docker_config: DockerConfig):
        uid = os.getuid()
        user = getpass.getuser()

        pulse_run_dir = get_existing_dir('Pulse run', [
            f'/run/user/{uid}/pulse',
            f'/run/{uid}/pulse',
        ])

        pulse_conf_dir = get_existing_dir('Pulse configuration', [
            f'/home/{user}/.pulse',
            f'/home/{user}/.config/pulse',
        ])

        docker_config.volumes.update({
            '/dev/shm': '/dev/shm',
            '/etc/machine-id': '/etc/machine-id',
            pulse_run_dir: '/run/user/1000/pulse',
            '/var/lib/dbus': '/var/lib/dbus',
            pulse_conf_dir: '/home/phablet/.pulse',
            '/dev/snd': '/dev/snd',
        })
