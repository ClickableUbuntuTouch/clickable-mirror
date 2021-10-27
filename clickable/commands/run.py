from clickable.exceptions import ClickableException
from clickable.container import Container

from .base import Command


class RunCommand(Command):
    def __init__(self):
        Command.__init__(self)
        self.cli_conf.name = 'run'
        self.cli_conf.help_msg = 'Runs an arbitrary command or opens a shell '\
            'in a temporary clickable container'

        self.root_user = True
        self.command = 'bash'
        self.lib = None

    def setup_parser(self, parser):
        parser.add_argument(
            '--user',
            action='store_true',
            help='Run as user (not as root)',
        )
        parser.add_argument(
            '--lib',
            help='Use library docker image',
        )
        parser.add_argument(
            'command',
            metavar='cmd',
            nargs='*',
            help='Command to run inside the container (defaults to bash)'
        )

    def configure(self, args):
        self.root_user = not args.user
        self.lib = args.lib

        if args.command:
            self.command = ' '.join(args.command)

    def configure_nested(self):
        raise ClickableException("Run command can't be nested in a chain.")

    def run(self):
        container = None

        if self.lib:
            for lib in self.config.lib_configs:
                if lib.name == self.lib:
                    container = Container(lib, lib.name)

            if not container:
                raise ClickableException(f'Library "{self.lib}" is not in your '
                                         'project config.')
        else:
            container = self.container

        container.setup()
        container.run_command(
            self.command,
            use_build_dir=False,
            tty=True,
            localhost=True,
            root_user=self.root_user,
        )
