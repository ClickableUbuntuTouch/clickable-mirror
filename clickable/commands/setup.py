from .base import Command
from clickable.logger import logger
from clickable.exceptions import ClickableException
from clickable.utils import run_subprocess_check_call, is_command

class SetupCommand(Command):
    def __init__(self):
        Command.__init__(self)
        self.cli_conf.name = 'setup'
        self.cli_conf.help_msg = 'Initial docker setup'

        self.setups = ['docker', 'completion', []]

    def setup_parser(self, parser):
        parser.add_argument(
            'setups',
            nargs='*',
            choices=self.setups,
            help='What to setup (defaults to everything)'
        )

    def configure(self, args):
        if args.setups:
            self.setups = args.setups

    def run(self):
        if 'docker' in self.setups:
            self.setup_docker()
        if 'completion' in self.setups:
            self.setup_bash_completion()

    def setup_docker(self):
        if self.container.is_docker_ready():
            logger.info('Docker is already set up')
            return

        if not self.confirm(
                'Do you want Clickable to set up docker by adding you to the docker group?'):
            return

        try:
            self.container.setup_docker()
            logger.info('Docker is set up and ready.')
        except ClickableException:
            logger.warning('Please log out or restart to apply changes')

    def find_argcomplete_command(self):
        command = 'register-python-argcomplete'

        if not is_command(command):
            command = 'register-python-argcomplete3'

        if not is_command(command):
            raise ClickableException('Cannot enable bash completion, because argcomplete is not installed.')

        return command

    def setup_bash_completion(self):
        if not self.confirm(
                'Do you want Clickable to set up bash completion by appending a line to your ~/.bashrc?'):
            logger.warning('Bash completion setup skipped. See https://kislyuk.github.io/argcomplete/ for how to enable completion manually, including other shells.')
            return

        argcomplete_command = self.find_argcomplete_command()
        activation = '\n# Enable bash completion for Clickable\neval "$({} clickable)"'.format(
                argcomplete_command)

        run_subprocess_check_call("echo '{}' >> ~/.bashrc".format(activation), shell=True)
        logger.info('Bash completion is set up. Open a new terminal to apply changes.')
