from clickable.commands.publish import PublishCommand
from .base_test import UnitTest


class TestPublishCommand(UnitTest):
    def setUp(self):
        self.command = PublishCommand()
        self.setUpConfig(commands="publish")


# TODO implement this
