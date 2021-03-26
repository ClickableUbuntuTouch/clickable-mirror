from .base import Builder
from clickable.config.project import ProjectConfig
from clickable.config.constants import Constants


class CustomBuilder(Builder):
    name = Constants.CUSTOM

    def build(self):
        for cmd in self.config.build:
            self.container.run_command(cmd)
