from clickable.logger import logger
from clickable.exceptions import ClickableException

from .desktop import DesktopCommand
from .idedelegates.qtcreator import QtCreatorDelegate
from .idedelegates.atom import AtomDelegate


class IdeCommand(DesktopCommand):
    def __init__(self):
        super().__init__()
        self.cli_conf.name = 'ide'
        self.cli_conf.help_msg = 'Run a custom command in desktop mode. '\
            'Some IDEs (QtCreator and Atom) are supported this way.'

        self.custom_mode = True
        self.ide_delegate = None
        self.list_support = False
        self.ide_support = True

    def setup_parser(self, parser):
        parser.add_argument(
            'command',
            metavar='cmd',
            default='qtcreator',
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
        self.command = ' '.join(args.command)
        self.ide_support = not args.no_support
        self.list_support = args.list_support

    def configure_nested(self):
        raise ClickableException("IDE command can't be nested in a chain.")

    def run(self):
        if self.list_support:
            logger.info("Supported IDEs are QtCreator (qtcreator) and Atom (atom).")
            return

        if self.ide_support:
            # get the preprocessor according to command if any
            if 'qtcreator' in self.command.split():
                self.ide_delegate = QtCreatorDelegate(self.config)
                self.command = self.ide_delegate.override_command(self.command)
                logger.debug(
                    'QtCreator command detected. Changing command to: {}'.format(self.command)
                )

            if 'atom' in self.command.split():
                self.ide_delegate = AtomDelegate(self.config)
                self.command = self.ide_delegate.override_command(self.command)
                logger.debug('Atom command detected. Changing command to: {}'.format(self.command))

        super().run()
