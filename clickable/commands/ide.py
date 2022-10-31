from clickable.logger import logger
from clickable.exceptions import ClickableException

from .desktop import DesktopCommand
from .idedelegates.qtcreator import QtCreatorDelegate


class IdeCommand(DesktopCommand):
    def __init__(self):
        super().__init__()
        self.cli_conf.name = 'ide'
        self.cli_conf.help_msg = 'Run a custom command in desktop mode. '\
            'Some IDEs (QtCreator) are supported this way.'

        self.custom_mode = True
        self.ide_delegate = None
        self.list_support = False
        self.ide_support = True

    def setup_parser(self, parser):
        parser.add_argument(
            'command',
            metavar='qtcreator',
            nargs='*',
            help='Command to run IDE inside the container',
        )
        parser.add_argument(
            '--no-support',
            action='store_true',
            help='Do not active IDE-specific support provided by Clickable',
        )
        parser.add_argument(
            '--list-support',
            action='store_true',
            help='List supported IDEs',
        )

    def configure(self, args):
        if args.command:
            self.command = ' '.join(args.command)
        elif self.config.global_config.ide.default:
            self.command = self.config.global_config.ide.default
        else:
            self.command = 'qtcreator'

        self.ide_support = not args.no_support
        self.list_support = args.list_support

        self.merge_image_setup()

    def configure_nested(self):
        raise ClickableException("IDE command can't be nested in a chain.")

    def merge_image_setup(self):
        ide_image_setup_run = self.config.global_config.ide.image_setup.get('run', [])
        if ide_image_setup_run:
            image_setup_run = self.config.image_setup.get('run', [])
            image_setup_run += ide_image_setup_run
            self.config.image_setup['run'] = image_setup_run

        ide_image_setup_env = self.config.global_config.ide.image_setup.get('env', {})
        if ide_image_setup_env:
            image_setup_env = self.config.image_setup.get('env', {})
            image_setup_env.update(ide_image_setup_env)
            self.config.image_setup['env'] = image_setup_env

    def run(self):
        if self.list_support:
            logger.info("Supported IDE is QtCreator (qtcreator)")
            return

        if self.ide_support:
            # get the preprocessor according to command if any
            if 'qtcreator' in self.command.split():
                self.ide_delegate = QtCreatorDelegate(self.config)
                self.command = self.ide_delegate.override_command(self.command)
                logger.debug(
                    'QtCreator command detected. Changing command to: %s', self.command
                )

        super().run()
