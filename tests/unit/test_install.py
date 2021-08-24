from unittest import mock
from unittest.mock import ANY

from clickable.commands.install import InstallCommand
from clickable.config.constants import Constants
from ..mocks import empty_fn, true_fn
from .base_test import UnitTest


class TestInstallCommand(UnitTest):
    def setUp(self):
        self.command = InstallCommand()
        self.setUpWithTmpBuildDir()

    @mock.patch('clickable.device.Device.check_any_adb_attached', side_effect=empty_fn)
    @mock.patch('clickable.device.Device.check_multiple_adb_attached', side_effect=empty_fn)
    @mock.patch('clickable.device.Device.run_command', side_effect=empty_fn)
    @mock.patch('clickable.commands.install.run_subprocess_check_call', side_effect=empty_fn)
    def test_install_adb(
        self,
        mock_run_subprocess_check_call,
        mock_run_command,
        mock_check_multiple_adb_attached,
        mock_check_any_adb_attached
    ):
        self.command.run()

        mock_check_any_adb_attached.assert_called_once_with()
        mock_check_multiple_adb_attached.assert_called_once_with()
        mock_run_subprocess_check_call.assert_called_once_with(
            'adb push /tmp/build/foo.bar_1.2.3_{}.click /home/phablet/'
            .format(Constants.host_arch),
            cwd='/tmp/build',
            shell=True
        )
        mock_run_command.assert_called_with(ANY, cwd='/tmp/build')

    @mock.patch('clickable.device.Device.check_any_adb_attached', side_effect=empty_fn)
    @mock.patch('clickable.device.Device.run_command', side_effect=empty_fn)
    @mock.patch('clickable.commands.install.run_subprocess_check_call', side_effect=empty_fn)
    def test_install_serial_number(
        self,
        mock_run_subprocess_check_call,
        mock_run_command,
        mock_check_any_adb_attached
    ):
        self.config.device_serial_number = 'foo'
        self.command.run()

        mock_check_any_adb_attached.assert_called_once_with()
        mock_run_subprocess_check_call.assert_called_once_with(
            'adb -s foo push /tmp/build/foo.bar_1.2.3_{}.click /home/phablet/'
            .format(Constants.host_arch),
            cwd='/tmp/build',
            shell=True
        )
        mock_run_command.assert_called_with(ANY, cwd='/tmp/build')

    @mock.patch('clickable.device.Device.run_command', side_effect=empty_fn)
    @mock.patch('clickable.commands.install.run_subprocess_check_call', side_effect=empty_fn)
    def test_install_scp(self, mock_run_subprocess_check_call, mock_run_command):
        self.config.ssh = 'foo'
        self.command.run()

        mock_run_subprocess_check_call.assert_called_once_with(
            'scp /tmp/build/foo.bar_1.2.3_{}.click phablet@foo:/home/phablet/'
            .format(Constants.host_arch),
            cwd='/tmp/build',
            shell=True
        )
        mock_run_command.assert_called_with(ANY, cwd='/tmp/build')

    @mock.patch('clickable.device.Device.check_any_adb_attached', side_effect=empty_fn)
    @mock.patch('clickable.device.Device.check_multiple_adb_attached', side_effect=empty_fn)
    @mock.patch('clickable.device.Device.run_command', side_effect=empty_fn)
    @mock.patch('clickable.commands.install.run_subprocess_check_call', side_effect=empty_fn)
    def test_install_adb_with_path(
        self,
        mock_run_subprocess_check_call,
        mock_run_command,
        mock_check_multiple_adb_attached,
        mock_check_any_adb_attached
    ):
        self.command.click_path = '/foo/bar.click'
        self.command.run()

        mock_check_any_adb_attached.assert_called_once_with()
        mock_check_multiple_adb_attached.assert_called_once_with()
        mock_run_subprocess_check_call.assert_called_once_with(
            'adb push /foo/bar.click /home/phablet/',
            cwd='.',
            shell=True
        )
        mock_run_command.assert_called_with(ANY, cwd='.')

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
