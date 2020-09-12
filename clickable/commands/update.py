import subprocess
import shlex

from clickable.config.constants import Constants
from .base import Command
from clickable.utils import (
    run_subprocess_check_call,
    run_subprocess_check_output,
    image_exists,
)

def update_image(image):
    if image_exists(image):
        command = 'docker pull {}'.format(image)
        run_subprocess_check_call(command)


class UpdateCommand(Command):
    def __init__(self):
        Command.__init__(self)
        self.cli_conf.aliases = ['update-images']
        self.cli_conf.name = 'update'
        self.cli_conf.help_msg = 'Update all Clickable docker images that have already been used'

    def run(self):
        self.container.check_docker()

        container_mapping = Constants.container_mapping[Constants.host_arch]
        for image in container_mapping.values():
            update_image(image)
