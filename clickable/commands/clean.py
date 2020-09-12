import os
import shutil
import sys

from .base import Command
from clickable.logger import logger


class CleanCommand(Command):
    def __init__(self):
        super().__init__()
        self.cli_conf.name = 'clean'
        self.cli_conf.help_msg = 'Clean the build directory'

    def run(self):
        if os.path.exists(self.config.build_dir):
            try:
                logger.info("Cleaning build dir {}.".format(self.config.build_dir))
                shutil.rmtree(self.config.build_dir)
            except Exception:
                cls, value, _ = sys.exc_info()
                if cls == OSError and 'No such file or directory' in str(value):  # TODO see if there is a proper way to do this
                    pass  # Nothing to do here, the directory didn't exist
                else:
                    logger.warning('Failed to clean the build directory: {}: {}'.format(type, value))

        if os.path.exists(self.config.install_dir):
            try:
                logger.info("Cleaning install dir {}.".format(self.config.build_dir))
                shutil.rmtree(self.config.install_dir)
            except Exception:
                cls, value, _ = sys.exc_info()
                if cls == OSError and 'No such file or directory' in str(value):  # TODO see if there is a proper way to do this
                    pass  # Nothing to do here, the directory didn't exist
                else:
                    logger.warning('Failed to clean the temp directory: {}: {}'.format(type, value))
