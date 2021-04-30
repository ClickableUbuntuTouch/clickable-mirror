from clickable.config.constants import Constants

from .base import Builder


class CustomBuilder(Builder):
    name = Constants.CUSTOM

    def build(self):
        for cmd in self.config.build:
            self.container.run_command(cmd)
