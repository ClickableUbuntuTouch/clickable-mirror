from unittest import mock
from unittest.mock import ANY

from clickable.commands.install import InstallCommand
from ..mocks import empty_fn, true_fn
from .base_test import UnitTest


class TestInstallCommand(UnitTest):
    def setUp(self):
        self.command = InstallCommand()
        self.setUpWithTmpBuildDir()

    @mock.patch('clickable.device.Device.push_file', side_effect=empty_fn)
    @mock.patch('clickable.device.Device.run_command', side_effect=empty_fn)
    def test_install(
        self,
        mock_run_command,
        mock_push_file,
    ):
        self.command.run()

        click_name = f'foo.bar_1.2.3_{self.command.config.arch}.click'
        mock_push_file.assert_called_once_with(
            f'/tmp/build/{click_name}',
            f'/home/phablet/{click_name}'
        )
        mock_run_command.assert_called_with(ANY, cwd='/tmp/build')

    @mock.patch('clickable.config.project.ProjectConfig.is_desktop_mode', side_effect=true_fn)
    @mock.patch('clickable.commands.install.logger.debug', side_effect=empty_fn)
    def test_skip_desktop_mode(self, mock_logger_debug, mock_desktop_mode):
        self.command.run()

        mock_logger_debug.assert_called_once_with(ANY)
        mock_desktop_mode.assert_called_once_with()

    @mock.patch('clickable.commands.install.logger.debug', side_effect=empty_fn)
    def test_skip_container_mode(self, mock_logger_debug):
        self.config.container_mode = True
        self.command.run()

        mock_logger_debug.assert_called_once_with(ANY)
