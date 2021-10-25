from clickable.utils import run_subprocess_check_call
from clickable.exceptions import ClickableException

from .base import Command


class ScriptCommand(Command):
    def __init__(self):
        Command.__init__(self)
        self.cli_conf.name = 'script'
        self.cli_conf.help_msg = 'Run a project-specific script'

        self.script_name = None

    def setup_parser(self, parser):
        parser.add_argument(
            'name',
            help='One of the scripts defined in the project config',
        )

    def configure(self, args):
        self.script_name = args.name

    def configure_nested(self):
        raise ClickableException("Script command can't be nested in a chain.")

    def run(self):
        command = self.config.scripts.get(self.script_name, None)

        if command:
            run_subprocess_check_call(command, shell=True)
        else:
            raise ClickableException(
                f'{self.script_name} is not a script defined in the project config.'
            )
