from .base import Command

from clickable.utils import run_subprocess_check_call
from clickable.exceptions import ClickableException

class ScriptCommand(Command):
    def __init__(self):
        Command.__init__(self)
        self.cli_conf.name = 'script'
        self.cli_conf.help_msg = 'Run a project-specific script'

        self.script_name = None

    def setup_parser(self, parser):
        parser.add_argument(
            'name',
            help='One of the scripts defined in the clickable.json',
        )

    def configure(self, args):
        self.script_name = args.name

    def configure_nested(self, args):
        raise ClickableException("Script command can't be nested in a chain.")

    def run(self):
        command = self.config.scripts.get(self.script_name, None)

        if command:
            run_subprocess_check_call(command)
        else:
            raise ClickableException('{} is not a script defined in the clickable.json.'.format(self.script_name))
