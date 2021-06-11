from unittest import mock

from clickable.commands.launch import LaunchCommand
from ..mocks import empty_fn, exception_fn
from .base_test import UnitTest


class TestLaunchCommand(UnitTest):
    def setUp(self):
        self.command = LaunchCommand()
        self.setUpWithTmpBuildDir()

    @mock.patch('clickable.device.Device.run_command', side_effect=empty_fn)
    def test_kill(self, mock_run_command):
        self.command.kill = 'foo and bar'
        self.command.try_kill()

        mock_run_command.assert_called_once_with('pkill -f \\"[f]oo and bar\\"')

    @mock.patch('clickable.device.Device.run_command', side_effect=exception_fn)
    def test_kill_ignores_exceptions(self, mock_run_command):
        self.command.kill = 'foo and bar'
        self.command.try_kill()

    @mock.patch('clickable.device.Device.run_command', side_effect=empty_fn)
    def test_launch(self, mock_run_command):
        self.command.run()

        mock_run_command.assert_called_once_with(
            'sleep 1s && ubuntu-app-launch foo.bar_foo_1.2.3',
            cwd='/tmp/build'
        )

    @mock.patch('clickable.device.Device.run_command', side_effect=empty_fn)
    def test_launch_custom(self, mock_run_command):
        self.config.launch = 'foo'
        self.command.run()

        mock_run_command.assert_called_once_with('sleep 1s && foo', cwd='/tmp/build')
