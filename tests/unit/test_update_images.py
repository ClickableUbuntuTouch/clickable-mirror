from unittest import mock
from unittest.mock import ANY

from clickable.commands.update_images import UpdateCommand
from ..mocks import empty_fn, false_fn
from .base_test import UnitTest

import pytest


@pytest.fixture(autouse=True)
def mock_function(monkeypatch):
    monkeypatch.setattr("clickable.container.Container.is_docker_desktop", false_fn)


def zero_fn(*args, **kwargs):
    return 0


def true_fn(*args, **kwargs):
    return True


class TestUpdateCommand(UnitTest):
    def setUp(self):
        self.command = UpdateCommand()
        self.setUpConfig(commands="update-images")

    @mock.patch('clickable.commands.clean_images.CleanImagesCommand.run', side_effect=empty_fn)
    @mock.patch('clickable.container.Container.check_docker', side_effect=empty_fn)
    @mock.patch('clickable.commands.update_images.image_exists', side_effect=true_fn)
    @mock.patch('clickable.commands.update_images.pull_image', side_effect=empty_fn)
    def test_update(
        self,
        mock_run_pull_image,
        mock_run_image_exists,
        mock_check_docker,
        mock_clean,
    ):
        self.command.run()

        mock_check_docker.assert_called_with()
        mock_run_image_exists.assert_called_with(ANY)
        mock_run_pull_image.assert_called_with(ANY, skip_existing=False)
        mock_clean.assert_called()
