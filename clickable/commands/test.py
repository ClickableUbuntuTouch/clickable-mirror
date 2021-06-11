from .base import Command


class TestCommand(Command):
    def __init__(self):
        Command.__init__(self)
        self.cli_conf.name = 'test'
        self.cli_conf.help_msg = 'Run the configured tests command on a virtual screen'

    def run(self):
        command = 'xvfb-startup {}'.format(self.config.test)

        self.container.run_command(command)
