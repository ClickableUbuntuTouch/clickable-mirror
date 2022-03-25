import os

from clickable.config.project import ProjectConfig
from clickable.config.constants import Constants
from clickable.config.file_helpers import InstallFiles
from clickable.config.global_config import GlobalConfig


class InstallFilesMock(InstallFiles):
    def write_manifest(self, *args):
        pass

    def get_manifest(self):
        return {
            'version': '1.2.3',
            'name': 'foo.bar',
            'architecture': '@CLICK_ARCH@',
            'hooks': {
                'foo': {
                    'desktop': '/fake/foo.desktop',
                },
            },
        }


class ConfigMock(ProjectConfig):
    def __init__(self,
                 mock_config_json=None,
                 mock_config_env=None,
                 mock_install_files=False,
                 respect_container_mode=False,
                 args=None,
                 commands=['build']):
        container_mode_key = "CLICKABLE_CONTAINER_MODE"

        if respect_container_mode:
            if (mock_config_env is not None and
                    container_mode_key not in mock_config_env and
                    container_mode_key in os.environ):
                mock_config_env[container_mode_key] = os.environ[container_mode_key]
        self.mock_config_json = mock_config_json
        self.mock_config_env = mock_config_env
        self.mock_install_files = mock_install_files

        super().__init__()
        super().configure(commands=commands, global_config=GlobalConfigMock(), args=args)

    def load_project_config(self, config_path):
        if self.mock_config_json is None:
            return super().load_project_config(config_path)

        config_json = self.mock_config_json
        return config_json

    def get_env_var(self, key):
        if self.mock_config_env is None:
            return super().get_env_var(key)

        return self.mock_config_env.get(key, None)

    def set_builder_interactive(self):
        if not self.config['builder'] and not self.needs_builder():
            self.config["builder"] = Constants.PURE

    def setup_helpers(self):
        super().setup_helpers()
        if self.mock_install_files:
            self.install_files = InstallFilesMock(
                self.config['install_dir'],
                self.config['builder'],
                self.config['arch'])


class GlobalConfigMock(GlobalConfig):
    def __init__(self):
        super().__init__(custom_path=None)

    def load(self, path, is_custom):
        return {}
