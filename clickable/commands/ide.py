from .desktop import DesktopCommand
from clickable.logger import logger
from clickable.exceptions import ClickableException
from .idedelegates.qtcreator import QtCreatorDelegate
from .idedelegates.atom import AtomDelegate

class IdeCommand(DesktopCommand):
    def __init__(self):
        super().__init__()
        self.cli_conf.name = 'ide'
        self.cli_conf.help_msg = 'Run a custom command in desktop mode (e.g. an IDE)'

        self.custom_mode = True
        self.ide_delegate = None

    def setup_parser(self, parser):
        parser.add_argument(
            'command',
            metavar='cmd',
            nargs='+',
            help='Command to run IDE inside the container',
        )

    def configure(self, args):
        self.command = ' '.join(args.command)

    def configure_nested(self):
        raise ClickableException("IDE command can't be nested in a chain.")

    def run(self):
        #get the preprocessor according to command if any
        if 'qtcreator' in self.command.split():
            self.ide_delegate = QtCreatorDelegate(self.config)
            self.command = self.ide_delegate.override_command(self.command)
            logger.debug('QtCreator command detected. Changing command to: {}'.format(self.command))

        if 'atom' in self.command.split():
            self.ide_delegate = AtomDelegate(self.config)
            self.command = self.ide_delegate.override_command(self.command)
            logger.debug('Atom command detected. Changing command to: {}'.format(self.command))

        super().run()
