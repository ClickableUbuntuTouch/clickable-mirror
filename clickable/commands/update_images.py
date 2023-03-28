from clickable.config.constants import Constants
from clickable.logger import logger
from clickable.utils import (
    pull_image,
    image_exists,
)

from .base import Command


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
            if image_exists(image):
                pull_image(image, skip_existing=False)

        logger.info('Update complete. '
                    'You may run "clickable clean-images" to delete obsolete ones.')
