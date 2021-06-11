from unittest import TestCase

from clickable.device import Device
from clickable.container import Container
from clickable.exceptions import ClickableException
from ..mocks import ConfigMock


class UnitTest(TestCase):
    def setUpWithTmpBuildDir(self):
        config_json = {}
        config_json["build_dir"] = "/tmp/build"
        config_json["install_dir"] = "/tmp/build/install"
        self.setUpConfig(mock_config_json=config_json)

    def setUpConfig(self,
                    expect_exception=False,
                    mock_config_json={},
                    mock_config_env={},
                    *args, **kwargs):
        self.config = None
        try:
            self.config = ConfigMock(
                mock_config_json=mock_config_json,
                mock_config_env=mock_config_env,
                mock_install_files=True,
                *args, **kwargs
            )
            self.config.interactive = False
            if self.command:
                self.command.config = self.config
                self.command.device = Device(self.config)
                self.command.container = Container(self.config)

            if expect_exception:
                raise ClickableException("A ClickableException was expected, but was not raised")
        except ClickableException as e:
            if not expect_exception:
                raise e

    def setUp(self):
        self.config = None
        self.command = None

    def tearDown(self):
        self.config = None
