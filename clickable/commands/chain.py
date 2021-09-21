from clickable.exceptions import ClickableException
from clickable.utils import env
from clickable.command_utils import get_commands
from clickable.config.project import ProjectConfig
from clickable.logger import logger

from .base import Command


class ChainCommand(Command):
    def __init__(self):
        super().__init__()
        self.cli_conf.aliases = ['default']
        self.cli_conf.name = 'chain'
        self.cli_conf.help_msg = 'Run a chain of commands'

        self.run_commands = []
        self.commands = []

    def setup_parser(self, parser):
        parser.add_argument(
            '--clean',
            action='store_true',
            help='Clean build directory before building',
            default=False,
        )
        parser.add_argument(
            'commands',
            nargs='*',
            help='List of commands to run (defaults to "build", "install", "launch" '
                 'if not set otherwise)',
        )

    def parse_common_options(self, args):
        self.commands = {c.cli_conf.name: c for c in get_commands()}
        self.run_commands = args.commands

        default_env = env('CLICKABLE_DEFAULT')
        if not self.run_commands and default_env:
            self.run_commands = default_env.split()

        self.config = ProjectConfig(args,
                                    commands=self.run_commands,
                                    always_clean=args.clean)

        self.run_commands = self.config.commands

    def configure_nested(self):
        raise ClickableException("Chain command can't be nested in a chain.")

    def run(self):
        logger.info('Going to run all of "%s"', '", "'.join(self.run_commands))

        for run in self.run_commands:
            if run not in self.commands:
                raise ClickableException(
                    f'Command {run} is unknown to Clickable')

            logger.info('Running command "%s"', run)

            command = self.commands[run]
            command.init_from_command(self)
            command.run()
