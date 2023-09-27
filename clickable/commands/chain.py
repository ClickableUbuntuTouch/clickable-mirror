from clickable.exceptions import ClickableException
from clickable.utils import env, flexible_string_to_list
from clickable.command_utils import get_commands
from clickable.logger import logger

from .base import Command


class ChainCommand(Command):
    def __init__(self):
        super().__init__()
        self.cli_conf.aliases = ['default']
        self.cli_conf.name = 'chain'
        self.cli_conf.help_msg = 'Run a chain of commands'
        self.command_conf.device_command = True

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
        self.load_configs(args)

        default_env = env('CLICKABLE_DEFAULT')
        self.commands = {c.cli_conf.name: c for c in get_commands()}

        if args.commands:
            self.run_commands = args.commands
        elif default_env:
            self.run_commands = default_env.split()
        elif self.global_config.cli.default_chain:
            self.run_commands = flexible_string_to_list(
                self.global_config.cli.default_chain, split=True)
        else:
            self.run_commands = 'build install launch'

        self.command_conf.device_command = False
        for cmd in self.run_commands:
            if cmd not in self.commands:
                raise ClickableException(
                    f'Command "{cmd}" is unknown to Clickable')

            if self.commands[cmd].command_conf.device_command:
                self.command_conf.device_command = True

            if self.commands[cmd].command_conf.arch_specific:
                self.command_conf.arch_specific = True

        self.create_device(args)
        device_arch = self.device.device_arch if self.device else None

        self.config.configure(
            self.global_config,
            self.run_commands,
            args,
            always_clean=args.clean,
            device_arch=device_arch)

    def configure_nested(self):
        raise ClickableException("Chain command can't be nested in a chain.")

    def run(self):
        logger.info('Going to run all of "%s"', '", "'.join(self.run_commands))

        for run in self.run_commands:
            logger.info('Running command "%s"', run)

            command = self.commands[run]
            command.init_from_command(self)
            command.run()
