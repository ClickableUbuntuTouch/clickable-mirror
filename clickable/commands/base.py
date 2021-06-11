from clickable.device import Device
from clickable.container import Container
from clickable.config.project import ProjectConfig
from clickable.config.command_cli import CommandCliConf
from clickable.utils import let_user_confirm


class Command():
    def __init__(self):
        self.device = None
        self.container = None
        self.config = None
        self.cli_conf = CommandCliConf()

    def init_from_command(self, command):
        self.config = command.config
        self.device = command.device
        self.container = command.container
        self.configure_nested()

    def parse_common_options(self, args):
        self.config = ProjectConfig(args, commands=[args.sub_command])

    def start(self, args):
        self.parse_common_options(args)

        self.setup()
        self.configure(args)
        self.run()

    def setup(self):
        self.device = Device(self.config)
        self.container = Container(self.config)

    def confirm(self, message, default=True):
        """ Let user confirm an action. Returns default in non-interactive mode. """
        if not self.config.interactive:
            return default

        return let_user_confirm(message, default)

    def setup_parser(self, parser):
        """ Set up command specific command line interface """
        # Implemented in subclasses

    def configure(self, args):
        """ Configure from command line interface with arguments """
        # Implemented in subclasses

    def configure_nested(self):
        """ Configure as nested command, e.g. when running chained """
        # Implemented in subclasses

    def run(self):
        """ Run command """
        raise NotImplementedError('run is not yet implemented')
