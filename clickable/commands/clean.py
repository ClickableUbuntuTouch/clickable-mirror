import os
import shutil
import sys

from clickable.logger import logger
from clickable.exceptions import ClickableException

from .base import Command


class CleanCommand(Command):
    def __init__(self, libs=None):
        super().__init__()
        self.cli_conf.name = 'clean'
        self.cli_conf.help_msg = 'Clean the build directory'

        self.app = True
        self.libs = libs

    def setup_parser(self, parser):
        parser.add_argument(
            '--app',
            action='store_true',
            help='Clean app build dir (only needed when using --libs as well)',
            default=False,
        )
        parser.add_argument(
            '--libs',
            nargs='*',
            help='Clean specified libs or all libs if none is specified',
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
            self.clean_libs()
        if self.app:
            self.clean_app()

    def clean_libs(self):
        if not self.config.lib_configs:
            logger.warning('No libraries defined.')
            return

        filter_libs = self.libs

        for lib in self.config.lib_configs:
            if lib.name in filter_libs or not filter_libs:
                logger.info("Cleaning {} build directory".format(lib.name))
                clean(lib.build_dir)

    def clean_app(self):
        logger.info("Cleaning app build directory")
        clean(self.config.build_dir)


def clean(path):
    if os.path.exists(path):
        try:
            logger.info("Cleaning directory {}.".format(path))
            shutil.rmtree(path)
        except Exception:  # pylint: disable=broad-except
            cls, value, _ = sys.exc_info()
            # TODO see if there is a proper way to do this
            if cls == OSError and 'No such file or directory' in str(value):
                pass  # Nothing to do here, the directory didn't exist
            else:
                logger.warning('Failed to clean the directory: {}: {}'.format(cls, value))
