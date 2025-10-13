from clickable.config.constants import Constants
from clickable.logger import logger
from clickable.utils import (
    pull_image,
    image_exists,
)

from .base import Command
from .clean_images import CleanImagesCommand


class UpdateCommand(Command):
    def __init__(self):
        Command.__init__(self)
        self.cli_conf.name = 'update-images'
        self.cli_conf.aliases = []
        self.cli_conf.help_msg = 'Update all Clickable docker images that have '\
            'already been used. This does not update Clickable itself.'

        self.auto_clean = False

    def setup_parser(self, parser):
        parser.add_argument(
            '--clean',
            action='store_true',
            help='Clean images after finishing update without asking.',
            default=False,
        )

    def configure(self, args):
        self.auto_clean = args.clean

    def run(self):
        self.container.check_docker()

        container_mapping = Constants.container_mapping[Constants.host_arch]
        for image in container_mapping.values():
            if image_exists(image):
                pull_image(image, skip_existing=False)

        logger.info('Update complete.')

        if self.auto_clean or self.confirm('Do you want to clean obsolete images now?'):
            clean_cmd = CleanImagesCommand()
            clean_cmd.init_from_command(self)
            clean_cmd.run()
        else:
            logger.info('You may run "clickable clean-images" to delete obsolete ones.')
