from clickable.utils import pull_image
from clickable.exceptions import ClickableException
from clickable.container import Container
from clickable.logger import logger
from clickable.config.constants import Constants

from .base import Command


class CiCommand(Command):
    def __init__(self):
        Command.__init__(self)
        self.cli_conf.name = 'ci'
        self.cli_conf.help_msg = 'Runs an arbitrary command or an interactive shell\
                in a temporary clickable CI container'

        self.root_user = True
        self.command = 'bash'
        self.version = None
        self.image = None

    def setup_parser(self, parser):
        parser.add_argument(
            '--user',
            action='store_true',
            help='Run as user (not as root)',
        )
        parser.add_argument(
            '--clickable-version',
            default='latest',
            help='Clickable version of CI image (defaults to latest, \
                    pulling before running the command)',
        )
        parser.add_argument(
            'command',
            metavar='cmd',
            nargs='*',
            help='Command to run inside the CI container, e.g. \
                    "-- clickable build -a arm64" (defaults to interactive shell)'
        )

    def determine_ci_image(self):
        image_framework = self.config.get_image_framework()
        image_name = Constants.ci_container_mapping.get(
            (image_framework, self.config.build_arch), None)

        if not image_name:
            raise ClickableException(
                f'There is currently no CI docker image for \
                        {image_framework}/{self.config.build_arch}')

        return f"{image_name}:{self.version}"

    def configure(self, args):
        self.root_user = not args.user
        self.version = args.clickable_version
        self.image = self.determine_ci_image()

        if args.command:
            self.command = ' '.join(args.command)

        if self.config.is_custom_docker_image:
            logger.warning("Ignoring custom docker image and using CI image instead.")

        self.config.docker_image = self.image
        self.config.is_custom_docker_image = True
        self.container = Container(self.config)

    def configure_nested(self):
        raise ClickableException("CI command can't be nested in a chain.")

    def run(self):
        logger.info("Running in container %s", self.image)

        if self.version == "latest":
            pull_image(self.image, skip_existing=False)

        self.container.setup()
        self.container.run_command(
            self.command,
            use_build_dir=False,
            tty=True,
            localhost=True,
            root_user=self.root_user,
        )
