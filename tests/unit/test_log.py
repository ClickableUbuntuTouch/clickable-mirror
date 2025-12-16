from unittest import mock
from unittest.mock import ANY

from clickable.commands.log import LogCommand
from ..mocks import empty_fn, true_fn
from .base_test import UnitTest


class TestLogCommand(UnitTest):
    def setUp(self):
        self.command = LogCommand()
        self.setUpConfig(commands="log")

    @mock.patch('clickable.device.Device.run_command', side_effect=empty_fn)
    def test_log(self, mock_run_command):
        self.command.run()
        mock_run_command.assert_called_once_with(
            'journalctl --user --no-pager -u '
            'lomiri-app-launch--application-click--foo.bar_foo_1.2.3--',
            get_output=True
        )

    @mock.patch('clickable.config.project.ProjectConfig.is_desktop_mode', side_effect=true_fn)
    @mock.patch('clickable.commands.log.logger.debug', side_effect=empty_fn)
    def test_no_desktop_mode_log(self, mock_logger_debug, mock_desktop_mode):
        self.command.run()

        mock_logger_debug.assert_called_once_with(ANY)
        mock_desktop_mode.assert_called_once_with()

    @mock.patch('clickable.commands.log.logger.debug', side_effect=empty_fn)
    def test_no_container_mode_log(self, mock_logger_debug):
        self.config.container_mode = True
        self.command.run()

        mock_logger_debug.assert_called_once_with(ANY)
