from unittest import mock
from unittest.mock import ANY

from clickable.commands.create import CreateCommand
from .base_test import UnitTest
from ..mocks import empty_fn


class TestCreateCommand(UnitTest):
    def setUp(self):
        self.command = CreateCommand()
        self.setUpConfig(commands="create")

    @mock.patch('cookiecutter.main.cookiecutter', side_effect=empty_fn)
    def test_create_interactive(self, mock_cookiecutter):
        self.config.interactive = True
        self.command.run()
        mock_cookiecutter.assert_called_with(
            ANY,
            extra_context={'Copyright Year': ANY},
            no_input=False,
            config_file=ANY,
            output_dir=ANY
        )

    @mock.patch('cookiecutter.main.cookiecutter', side_effect=empty_fn)
    def test_create_non_interactive(self, mock_cookiecutter):
        self.config.interactive = False
        self.command.run()
        mock_cookiecutter.assert_called_with(
            ANY,
            extra_context={'Copyright Year': ANY},
            no_input=True,
            config_file=ANY,
            output_dir=ANY
        )

# TODO add more
