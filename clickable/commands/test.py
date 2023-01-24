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

        self.app = True
        self.libs = None

    def setup_parser(self, parser):
        parser.add_argument(
            '--app',
            action='store_true',
            help='Run app tests (only needed when using --libs as well)',
            default=False,
        )
        parser.add_argument(
            '--libs',
            nargs='*',
            help='Test specified libs or all libs if none is specified',
            default=None,
        )

    def configure(self, args):
        self.app = args.app or args.libs is None
        self.libs = args.libs

        if self.libs is not None:
            existing_libs = [lib.name for lib in self.config.lib_configs]
            for lib in self.libs:
                if lib not in existing_libs:
                    raise ClickableException(
                        f'Cannot test unknown library "{lib}", which is not in your '
                        'project config'
                    )

    def run(self):
        if self.libs is not None:
            self.test_libs()
        if self.app:
            logger.info("Running app tests")
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
