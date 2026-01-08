from clickable.logger import logger
from clickable.exceptions import ClickableException
from clickable.container import Container

from clickable.utils import (
    get_builder,
)

from .base import Command


class TestCommand(Command):
    def __init__(self):
        Command.__init__(self)
        self.cli_conf.name = 'test'
        self.cli_conf.help_msg = 'Run the configured tests command on a virtual screen'

        self.app = False
        self.libs = None

    def setup_parser(self, parser):
        parser.add_argument(
            '--app',
            action='store_true',
            help='Run app tests '
            '(default if project contains an app and nothing else specified)',
            default=False,
        )
        parser.add_argument(
            '--libs',
            nargs='*',
            help='Test specified libs or all libs if none is specified. '
            'Enabled by default, if the project does not contain an app.',
            default=None,
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Test libraries and app (equivalent to --libs and --app '
            'if project contains an app)',
            default=False,
        )

    def configure(self, args):
        self.app = args.app
        self.libs = args.libs

        if (args.all or args.libs is None) and self.config.is_app:
            self.app = True
        if args.all:
            # Empty list implies all libs are tested
            self.libs = []

        self.configure_common()

        if self.libs is not None:
            existing_libs = [lib.name for lib in self.config.lib_configs]
            for lib in self.libs:
                if lib not in existing_libs:
                    options = ", ".join(existing_libs)
                    raise ClickableException(
                        f'Cannot test unknown library "{lib}", which is not in your '
                        f'project config. Valid options: {options}'
                    )

    def configure_nested(self):
        if self.config.is_app:
            self.app = True

        self.configure_common()

    def configure_common(self):
        if self.app and not self.config.is_app:
            raise ClickableException("Cannot test app when project does not contain an app")

        if not self.config.is_app and self.libs is None:
            # Empty list implies all libs are built
            logger.info("Testing libs, because project does not contain an app")
            self.libs = []

    def run(self):
        if self.libs is not None:
            self.test_libs()
        if self.app:
            logger.info("Running app tests")
            self.container.setup()
            run_test(self.container, self.config)

    def test_libs(self):
        if not self.config.lib_configs:
            logger.warning('No libraries defined.')
            return

        filter_libs = self.libs

        for lib in self.config.lib_configs:
            if lib.name in filter_libs or not filter_libs:
                logger.info("Running tests on %s", lib.name)

                self.test_single_lib(lib)

    def test_single_lib(self, lib):
        lib.container = Container(lib, lib.name)
        lib.container.setup()

        # This is a workaround for lib env vars being overwritten by
        # project env vars, especially affecting Container Mode.
        lib.set_env_vars()

        run_test(lib.container, lib, is_app=False)


def run_test(container, config, is_app=True):
    builder = get_builder(config, container)
    builder.test(is_app)
