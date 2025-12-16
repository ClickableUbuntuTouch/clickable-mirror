from clickable.commands.shell import ShellCommand
from .base_test import UnitTest


class TestShellCommand(UnitTest):
    def setUp(self):
        self.command = ShellCommand()
        self.setUpConfig(commands="shell")


# TODO implement this
