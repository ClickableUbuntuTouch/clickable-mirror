from unittest import mock

from clickable.commands.review import ReviewCommand
from ..mocks import empty_fn
from .base_test import UnitTest


class TestReviewCommand(UnitTest):
    def setUp(self):
        self.command = ReviewCommand()
        self.setUpWithTmpBuildDir()

    @mock.patch('clickable.container.Container.run_command', side_effect=empty_fn)
    def test_run(self, mock_run_command):
        self.command.run()

        mock_run_command.assert_called_once_with(
            'click-review /tmp/build/foo.bar_1.2.3_{}.click'.format(self.config.arch),
            cwd='/tmp/build',
            use_build_dir=False
        )

    @mock.patch('clickable.container.Container.run_command', side_effect=empty_fn)
    def test_run_with_path_arg(self, mock_run_command):
        self.command.click = '/foo/bar.click'
        self.command.run()

        mock_run_command.assert_called_once_with(
            'click-review /foo/bar.click',
            cwd='/foo',
            use_build_dir=False
        )
