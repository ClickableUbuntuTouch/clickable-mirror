import os
import sys

from .base import Command
from clickable.logger import logger
from clickable.utils import get_builders, run_subprocess_check_call, env
from clickable.container import Container
from clickable.exceptions import ClickableException


class LibBuildCommand(Command):
    def __init__(self):
        super().__init__()
        self.cli_conf.name = 'build-libs'
        self.cli_conf.help_msg = 'Compile the library dependencies'

        self.debug_build = False
        self.libs = []

    def setup_parser(self, parser):
        parser.add_argument(
            '--debug',
            action='store_true',
            help='Perform a debug build',
            default=False,
        )
        parser.add_argument(
            'libs',
            nargs='*',
            help='Only build specified libs'
        )

    def configure(self, args):
        self.debug_build = args.debug
        self.libs = args.libs

        existing_libs = [lib.name for lib in self.config.lib_configs]

        for lib in self.libs:
            if lib not in existing_libs:
                raise ClickableException('Cannot build unknown library "{}", which is not in your clickable.json'.format(lib))

        self.parse_env()

    def configure_nested(self):
        self.parse_env()

    def parse_env(self):
        if env('CLICKABLE_DEBUG_BUILD'):
            self.debug_build = True
            self.config.debug_build = True
            self.config.env_vars['DEBUG_BUILD'] = '1'

            for lib in self.config.lib_configs:
                lib.env_vars['DEBUG_BUILD'] = '1'

    def run(self):
        if not self.config.lib_configs:
            logger.warning('No libraries defined.')

        filter_libs = self.libs

        for lib in self.config.lib_configs:
            if lib.name in filter_libs or not filter_libs:
                logger.info("Building {}".format(lib.name))

                lib.container_mode = self.config.container_mode
                lib.docker_image = self.config.docker_image
                lib.build_arch = self.config.build_arch
                lib.container = Container(lib, lib.name)
                lib.container.setup()

                # This is a workaround for lib env vars being overwritten by
                # project env vars, especially affecting Container Mode.
                lib.set_env_vars()

                try:
                    os.makedirs(lib.build_dir, exist_ok=True)
                except Exception:
                    logger.warning('Failed to create the build directory: {}'.format(str(sys.exc_info()[0])))

                try:
                    os.makedirs(lib.build_home, exist_ok=True)
                except Exception:
                    logger.warning('Failed to create the build home directory: {}'.format(str(sys.exc_info()[0])))

                if lib.prebuild:
                    run_subprocess_check_call(lib.prebuild, cwd=self.config.cwd, shell=True)

                self.build(lib)

                if lib.postbuild:
                    run_subprocess_check_call(lib.postbuild, cwd=lib.build_dir, shell=True)

    def build(self, lib):
        builder_classes = get_builders()
        builder = builder_classes[lib.builder](lib, lib.container, self.debug_build)
        builder.build()
