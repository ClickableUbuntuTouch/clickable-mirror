import os

from clickable.logger import logger
from clickable.container import Container
from clickable.exceptions import ClickableException

from .base import Command


class TestLibsCommand(Command):
    def __init__(self):
        super().__init__()
        self.cli_conf.name = 'test-libs'
        self.cli_conf.help_msg = 'Run tests on libraries'

        self.libs = []

    def setup_parser(self, parser):
        parser.add_argument(
            'libs',
            nargs='*',
            help='Only test specified libs'
        )

    def configure(self, args):
        self.libs = args.libs

        existing_libs = [lib.name for lib in self.config.lib_configs]

        for lib in self.libs:
            if lib not in existing_libs:
                raise ClickableException(
                    'Cannot test unknown library "{}", which is not in your clickable.json'.format(
                        lib
                    )
                )

    def run(self):
        if not self.config.lib_configs:
            logger.warning('No libraries defined.')

        filter_libs = self.libs

        for lib in self.config.lib_configs:
            if lib.name in filter_libs or not filter_libs:
                logger.info("Running tests on {}".format(lib.name))

                self.run_test(lib)

    def run_test(self, lib):
        if not os.path.exists(lib.build_dir):
            logger.warning(
                "Library {} has not yet been built for host architecture.".format(lib.name)
            )
        else:
            lib.container_mode = self.config.container_mode
            lib.docker_image = self.config.docker_image
            lib.build_arch = self.config.build_arch
            lib.container = Container(lib, lib.name)
            lib.container.setup()

            # This is a workaround for lib env vars being overwritten by
            # project env vars, especially affecting Container Mode.
            lib.set_env_vars()

            command = 'xvfb-startup {}'.format(lib.test)
            lib.container.run_command(command, use_build_dir=True)
