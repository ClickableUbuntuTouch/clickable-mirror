import os
import re

from clickable.config.constants import Constants
from clickable.logger import logger
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
        if not self.container.is_docker():
            logger.info('Not using Docker, Docker set up not required')
            return
        if self.container.is_docker_ready():
            logger.info('Docker is already set up')
            return

        if not self.confirm(
                'Do you want Clickable to set up docker by adding you to the docker group?\n'
                'See https://docs.docker.com/engine/security/#docker-daemon-attack-surface '
                'for security implications.'):
            return

        self.container.setup_docker()
        logger.info('Docker is set up and ready.')

    def setup_bash_completion(self):
        bashrc_file = os.path.join(Constants.host_home, '.bashrc')
        search = re.compile(r"[^#]*register-python-argcomplete3? clickable\b(?![-]).*")
        source_hint = f'Run "source {bashrc_file}" or open a new terminal to apply changes.'

        try:
            with open(bashrc_file, "r", encoding='UTF-8') as f:
                for line in f.readlines():
                    if search.match(line):
                        logger.info('Bash completion seems to be already set up.')
                        logger.info(source_hint)
                        return
        except FileNotFoundError:
            logger.warning('%s not found. Clickable can create it for you.',
                           bashrc_file)
            logger.warning(
                'If you are not using Bash, check %s for how to set up completion',
                'https://kislyuk.github.io/argcomplete/')

        if not self.confirm(
            'Do you want Clickable to set up bash completion by appending an '
            f'argcomplete command to your {bashrc_file}?'
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

        run_subprocess_check_call(f"echo '\n{activation}' >> {bashrc_file}", shell=True)
        logger.info('Bash completion is set up.')
        logger.info(source_hint)
