from clickable.config.constants import Constants
from clickable.utils import (
    run_subprocess_check_call,
    image_exists,
)

from .base import Command


def update_image(image):
    if image_exists(image):
        command = f'docker pull {image}'
        run_subprocess_check_call(command)


class UpdateCommand(Command):
    def __init__(self):
        Command.__init__(self)
        self.cli_conf.name = 'update-images'
        self.cli_conf.aliases = []
        self.cli_conf.help_msg = 'Update all Clickable docker images that have '\
            'already been used. This does not update Clickable itself.'

    def run(self):
        self.container.check_docker()

        container_mapping = Constants.container_mapping[Constants.host_arch]
        for image in container_mapping.values():
            update_image(image)
