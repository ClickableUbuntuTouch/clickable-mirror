import argparse
import sys

from clickable.version import show_version
from clickable.exceptions import ClickableException


class VersionAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        show_version()
        sys.exit(0)


class Cli():
    def __init__(self):
        self.parser = argparse.ArgumentParser(description='clickable')
        self.subparsers = self.parser.add_subparsers(title='commands', dest='sub_command')

        self.parser.add_argument('--version', '-v', nargs=0, action=VersionAction)

    def add_cmd_parser(self, command):
        config = command.cli_conf

        if not config.name:
            raise ClickableException("Command class {} has no command name.".format(
                type(command).__name__))

        parser = self.subparsers.add_parser(
            config.name,
            help=config.help_msg,
            aliases=config.aliases
        )

        self.add_common_options(parser)
        command.setup_parser(parser)

        parser.set_defaults(func=command.start)

    def add_common_options(self, parser):
        parser.add_argument(
            '--config',
            '-c',
            help='Use specified config file instead of looking for the optional "clickable.json" '
                 'in the current directory',
            default=None
        )
        parser.add_argument(
            '--serial-number',
            '-s',
            help='Directs command to the device or emulator with the given serial number or '
                 'qualifier (using adb)',
            default=None
        )
        parser.add_argument(
            '--ssh',
            help='Directs command to the device with the given IP address (using ssh)',
            default=None
        )
        parser.add_argument(
            '--arch',
            '-a',
            choices=['armhf', 'arm64', 'amd64', 'all'],
            help='Use the specified arch when building'
        )
        parser.add_argument(
            '--container-mode',
            action='store_true',
            help='Run all build commands on the current machine and not a container',
            default=False,
        )
        parser.add_argument(
            '--docker-image',
            help='Use a specific docker image to build with'
        )
        parser.add_argument(
            '--nvidia',
            action='store_true',
            help='Use docker with --runtime=nvidia and *-nvidia docker image',
            default=False,
        )
        parser.add_argument(
            '--no-nvidia',
            action='store_true',
            help="Don't use docker with --runtime=nvidia and *-nvidia docker image "
                 "(disables automatic nvidia detection)",
            default=False,
        )
        parser.add_argument(
            '--non-interactive',
            action='store_true',
            help='Do not show prompts for anything (meant for CIs and integration '
                 'into other tools)',
            default=False,
        )

        self.add_verbose_option(parser)

    def add_verbose_option(self, parser):
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Allows to debug clickable by enabling verbose output',
            default=False,
        )

    def parse_args(self, argv):
        return self.parser.parse_args(argv)