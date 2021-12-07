from clickable.exceptions import ClickableException
from clickable.container import Container
from clickable.logger import logger

from .base import Command
from .update_images import update_image


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
            '--dev',
            action='store_true',
            help='Run the nightly dev channel of Clickable',
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

    def configure(self, args):
        self.root_user = not args.user
        self.version = args.clickable_version
        name = "ci-dev-16.04" if args.dev else "ci-16.04"
        self.image = f"clickable/{name}-{self.config.build_arch}:{self.version}"

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
            update_image(self.image)

        self.container.setup()
        self.container.run_command(
            self.command,
            use_build_dir=False,
            tty=True,
            localhost=True,
            root_user=self.root_user,
        )
