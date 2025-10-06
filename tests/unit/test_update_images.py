from unittest import mock
from unittest.mock import ANY

from clickable.commands.update_images import UpdateCommand
from ..mocks import empty_fn
from .base_test import UnitTest


def zero_fn(*args, **kwargs):
    return 0


def true_fn(*args, **kwargs):
    return True


class TestUpdateCommand(UnitTest):
    def setUp(self):
        self.command = UpdateCommand()
        self.setUpConfig()

    @mock.patch('clickable.container.Container.check_docker', side_effect=empty_fn)
    @mock.patch('clickable.commands.update_images.image_exists', side_effect=true_fn)
    @mock.patch('clickable.commands.update_images.pull_image', side_effect=empty_fn)
    def test_update(
        self,
        mock_run_pull_image,
        mock_run_image_exists,
        mock_check_docker
    ):
        self.command.run()

        mock_check_docker.assert_called_with()
        mock_run_image_exists.assert_called_with(ANY)
        mock_run_pull_image.assert_called_with(ANY, skip_existing=False)
