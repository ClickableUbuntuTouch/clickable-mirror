from clickable.logger import logger
from clickable.exceptions import ClickableException
from clickable.utils import run_subprocess_check_call

from .base import Command


class SetupCommand(Command):
    def __init__(self):
        Command.__init__(self)
        self.cli_conf.name = 'setup'
        self.cli_conf.help_msg = 'Interactively set up autocompletion and docker'

        self.setups = ['docker', 'completion', []]

    def setup_parser(self, parser):
        parser.add_argument(
            'setups',
            nargs='*',
            choices=self.setups,
            help='What to set up (defaults to everything)'
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

    def setup_bash_completion(self):
        if not self.confirm(
            'Do you want Clickable to set up bash completion by appending an '
            'argcomplete command to your ~/.bashrc?'
        ):
            logger.warning(
                'Bash completion setup skipped. See https://kislyuk.github.io/argcomplete/ '
                'for how to enable completion for different shells.'
            )
            return

        activation = '''
# Enable bash completion for Clickable
if [ $(command -v register-python-argcomplete) ]; then
  eval "$(register-python-argcomplete clickable)"
elif [ $(command -v register-python-argcomplete3) ]; then
  eval "$(register-python-argcomplete3 clickable)"
else
  echo "Cannot enable Clickable autocompletion, because argcomplete is not installed"
fi
'''.strip()

        run_subprocess_check_call(f"echo '\n{activation}' >> ~/.bashrc", shell=True)
        logger.info('Bash completion is set up. Run "source ~/.bashrc" or open a new '
                    'terminal to apply changes.')
