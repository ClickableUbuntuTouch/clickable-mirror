from clickable.commands.docker.docker_config import DockerConfig
from .docker_support import DockerSupport


class DebugGdbSupport(DockerSupport):
    def __init__(self, port):
        self.port = port

    def update(self, docker_config: DockerConfig):
        if self.port:
            docker_config.execute = 'gdbserver localhost:{} {}'.format(
                self.port,
                docker_config.execute
            )
            docker_config.add_extra_options({
                '--publish': '{port}:{port}'.format(port=self.port)
            })
        else:
            docker_config.execute = 'gdb --args {}'.format(docker_config.execute)
            docker_config.add_extra_options({
                '--cap-add': 'SYS_PTRACE',
                '--security-opt seccomp': 'unconfined'
            })
