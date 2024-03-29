from unittest import TestCase, mock
import multiprocessing

from clickable.config.project import Constants
from ..mocks import ConfigMock, true_fn


class TestConfigCommand(TestCase):
    def setUp(self):
        self.config = ConfigMock(mock_config_env={})
        self.config.arch = None
        self.config.make_jobs = None

    def test_set_conditional_defaults_default(self):
        self.config.container_mode = False
        self.config.set_conditional_defaults(device_arch=None)
        self.assertEqual(self.config.arch, Constants.host_arch)
        self.assertEqual(self.config.make_jobs, str(multiprocessing.cpu_count()))

    def test_set_conditional_defaults_make_args(self):
        self.config.make_args = 'test -j5 and more stuff'

        self.config.set_conditional_defaults(device_arch=None)
        self.assertEqual(self.config.make_jobs, '5')

    def test_set_conditional_defaults_container_mode(self):
        self.config.host_arch = Constants.host_arch
        self.config.container_mode = True

        self.config.set_conditional_defaults(device_arch=None)
        self.assertEqual(self.config.arch, Constants.host_arch)

    def test_set_conditional_defaults_arch_agnostic(self):
        self.config.builder = Constants.PURE_QML_CMAKE

        self.config.set_conditional_defaults(device_arch=None)
        self.assertEqual(self.config.arch, 'all')

    @mock.patch('clickable.config.project.ProjectConfig.is_desktop_mode', side_effect=true_fn)
    def test_set_conditional_defaults_arch_desktop(self, mock_desktop_mode):
        self.config.set_conditional_defaults(device_arch=None)
        self.assertEqual(self.config.arch, Constants.host_arch)
        mock_desktop_mode.assert_called_once_with()

    def test_set_conditional_defaults_restrict_arch(self):
        self.config.restrict_arch = 'arm64'

        self.config.set_conditional_defaults(device_arch=None)
        self.assertEqual(self.config.arch, 'arm64')

    def test_set_conditional_defaults_restrict_arch_env(self):
        self.config.restrict_arch_env = 'arm64'

        self.config.set_conditional_defaults(device_arch=None)
        self.assertEqual(self.config.arch, 'arm64')
