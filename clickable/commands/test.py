import os

from clickable.logger import logger
from clickable.exceptions import ClickableException
from clickable.container import Container

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
                        'Cannot clean unknown library "{}", which is not in your '
                        'clickable.json'.format(lib)
                    )

    def run(self):
        if self.libs is not None:
            self.test_libs()
        if self.app:
            logger.info("Running app tests")
            test(self.container, self.config)

    def test_libs(self):
        if not self.config.lib_configs:
            logger.warning('No libraries defined.')

        filter_libs = self.libs

        for lib in self.config.lib_configs:
            if lib.name in filter_libs or not filter_libs:
                logger.info("Running tests on {}".format(lib.name))

                self.test_single_lib(lib)

    def test_single_lib(self, lib):
        lib.container_mode = self.config.container_mode
        lib.docker_image = self.config.docker_image
        lib.build_arch = self.config.build_arch
        lib.container = Container(lib, lib.name)
        lib.container.setup()

        # This is a workaround for lib env vars being overwritten by
        # project env vars, especially affecting Container Mode.
        lib.set_env_vars()

        test(lib.container, lib)


def test(container, config):
    if not os.path.exists(config.build_dir):
        raise ClickableException("Build dir does not exist. Run build command before testing.")

    command = 'xvfb-startup {}'.format(config.test)
    container.run_command(command, use_build_dir=True)
