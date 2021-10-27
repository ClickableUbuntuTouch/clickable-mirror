import os

from clickable.logger import logger
from clickable.exceptions import ClickableException


class Builder():
    name = None

    def __init__(self, config, container, debug_build):
        self.config = config
        self.container = container
        self.debug_build = debug_build

    def test(self, is_app=True):
        # May be overriden by some builders

        if not os.path.exists(self.config.build_dir):
            raise ClickableException("Build dir does not exist. Run build command before testing.")

        test = self.config.test
        if not test:
            if is_app:
                test = "qmltestrunner"
            else:
                test = "ctest"
            logger.info("No test command defined. Defaulting to %s", test)

        command = f'xvfb-startup {test}'
        self.container.run_command(command, use_build_dir=not is_app)

    def build(self):
        raise NotImplementedError()
