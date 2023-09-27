from unittest import TestCase
import os
import shutil

from clickable.cli import Cli
from clickable.container import Container
from clickable.config.device import DeviceConfig
from clickable.device import Device
from clickable.exceptions import ClickableException
from clickable.command_utils import get_commands
from ..mocks import ConfigMock


class IntegrationTest(TestCase):
    def setUpConfig(self,
                    expect_exception=False,
                    mock_config_json={},
                    mock_config_env={},
                    *args, **kwargs):
        self.setUpTestDir()

        self.config = None
        try:
            self.config = ConfigMock(
                mock_config_json=mock_config_json,
                mock_config_env=mock_config_env,
                mock_install_files=True,
                respect_container_mode=True,
                *args, **kwargs
            )
            self.config.interactive = False
            if self.command:
                self.command.config = self.config
                self.command.device = Device(DeviceConfig(base={'selection': 'host'}))
                self.command.container = Container(self.config)

            if expect_exception:
                raise ClickableException("A ClickableException was expected, but was not raised")
        except ClickableException as e:
            if not expect_exception:
                raise e

    def setUpTestDir(self):
        self.test_dir = os.path.abspath("tests/tmp")
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def setUp(self):
        self.clickable = None
        self.command = None
        self.config = None
        self.setUpTestDir()

    def tearDown(self):
        self.clickable = None
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def run_command(
        self,
        cli_args=[],
        expect_exception=False
    ):
        """
        Generic test run function

        :param list cli_args: additional cli args to call clickable with
        :param bool expect_exception: asserts an ClickableException to be raised
                    (True) or not to be raised (False)
        """

        if not self.command:
            raise ClickableException('No command set in integration test')

        cli = Cli()
        for cmd in get_commands():
            cli.add_cmd_parser(cmd)
        args = cli.parse_args([self.command.cli_conf.name] + cli_args)

        try:
            self.command.start(args)
            if expect_exception:
                raise ClickableException("A ClickableException was expected, but was not raised")
        except ClickableException as e:
            if not expect_exception:
                raise e
