import os
import shutil
import sys

from .base import Command
from clickable.logger import logger
from clickable.exceptions import ClickableException


class CleanLibsCommand(Command):
    def __init__(self):
        super().__init__()
        self.cli_conf.name = 'clean-libs'
        self.cli_conf.help_msg = 'Clean the library build directories'

        self.libs = []

    def setup_parser(self, parser):
        parser.add_argument(
            'libs',
            nargs='*',
            help='Only clean specified libs'
        )

    def configure(self, args):
        self.libs = args.libs

        existing_libs = [lib.name for lib in self.config.lib_configs]

        for lib in self.libs:
            if lib not in existing_libs:
                raise ClickableException('Cannot clean unknown library "{}", which is not in your clickable.json'.format(lib))

    def run(self):
        if not self.config.lib_configs:
            logger.warning('No libraries defined.')

        filter_libs = self.libs

        for lib in self.config.lib_configs:
            if lib.name in filter_libs or not filter_libs:
                logger.info("Cleaning {}".format(lib.name))

                if os.path.exists(lib.build_dir):
                    try:
                        shutil.rmtree(lib.build_dir)
                    except Exception:
                        cls, value, traceback = sys.exc_info()
                        if cls == OSError and 'No such file or directory' in str(value):  # TODO see if there is a proper way to do this
                            pass  # Nothing to do here, the directory didn't exist
                        else:
                            logger.warning('Failed to clean the build directory: {}: {}'.format(type, value))
                else:
                    logger.warning('Nothing to clean. Path does not exist: {}'.format(lib.build_dir))

