from unittest import mock

from clickable.commands.run import RunCommand
from ..mocks import empty_fn, false_fn
from .base_test import UnitTest

import pytest


@pytest.fixture(autouse=True)
def mock_function(monkeypatch):
    monkeypatch.setattr("clickable.container.Container.is_docker_desktop", false_fn)


class TestRunCommand(UnitTest):
    def setUp(self):
        self.command = RunCommand()
        self.setUpConfig(commands="run")

    @mock.patch('clickable.container.Container.run_command', side_effect=empty_fn)
    @mock.patch('clickable.container.Container.setup', side_effect=empty_fn)
    def test_run(self, mock_setup, mock_run_command):
        self.command.command = 'echo foo'
        self.command.run()

        mock_setup.assert_called_once_with()
        mock_run_command.assert_called_once_with(
            'echo foo',
            use_build_dir=False,
            tty=True,
            localhost=True,
            root_user=True
        )

    @mock.patch('clickable.container.Container.run_command', side_effect=empty_fn)
    @mock.patch('clickable.container.Container.setup', side_effect=empty_fn)
    def test_run_default_command(self, mock_setup, mock_run_command):
        self.command.run()

        mock_setup.assert_called_once_with()
        mock_run_command.assert_called_once_with(
            'bash',
            use_build_dir=False,
            tty=True,
            localhost=True,
            root_user=True
        )
