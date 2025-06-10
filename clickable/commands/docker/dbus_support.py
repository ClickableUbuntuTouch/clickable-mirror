from clickable.commands.docker.docker_config import DockerConfig
from clickable.utils import get_existing_dir
from .docker_support import DockerSupport


class DBusSupport(DockerSupport):
    def update(self, docker_config: DockerConfig):
        if docker_config.dbus:
            dbus_run = get_existing_dir('DBus run', [
                '/run/dbus',
                '/var/run/dbus'
            ])

            docker_config.add_volume_mappings({
                '/run/dbus': dbus_run
            })
