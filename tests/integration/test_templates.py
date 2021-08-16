import os
import shutil
import yaml
from os.path import join

from clickable.commands.create import CreateCommand
from clickable.commands.build import BuildCommand
from .base_test import IntegrationTest


class TestTemplates(IntegrationTest):
    def setUp(self):
        self.command = BuildCommand()
        self.setUpConfig(mock_config_env={'GOPATH': '/tmp/gopath'})

        self.original_path = os.getcwd()
        self.app_path = os.path.abspath(os.path.join(self.test_dir, 'appname'))

        os.makedirs(self.test_dir)
        os.chdir(self.test_dir)

        self.config_file = os.path.expanduser('~/.clickable/cookiecutter_config.yaml')
        self.tmp_config_file = '/tmp/cookiecutter_config.yaml'
        self.restore_config = False
        if os.path.exists(self.config_file):
            shutil.move(self.config_file, self.tmp_config_file)
            self.restore_config = True

    def tearDown(self):
        super().tearDown()
        os.chdir(self.original_path)

        if self.restore_config:
            shutil.move(self.tmp_config_file, self.config_file)

    def create_and_run(self, template, arch):
        create_command = CreateCommand()
        create_command.config = self.config
        create_command.extra_context['Template'] = template
        create_command.run()

        os.chdir(self.app_path)

        if template == 'Go':
            clickable_path = join(self.app_path, 'clickable.json')
            with open(clickable_path, 'r') as f:
                clickableConfig = yaml.safe_load(f)

            clickableConfig['prebuild'] = 'cd $ROOT && \
                GOPATH=/tmp/gopath GOBIN=$GOPATH/bin /usr/local/go/bin/go get'

            with open(clickable_path, 'w') as f:
                yaml.dump(clickableConfig, f)

        self.run_command(
            cli_args=['--arch', arch, '--clean'],
        )

    def assertClickExists(self, arch):
        click = os.path.join(
            self.app_path,
            'build/x86_64-linux-gnu/app/appname.yourname_1.0.0_amd64.click'
        )
        if arch == 'all':
            click = os.path.join(self.app_path, 'build/all/app/appname.yourname_1.0.0_all.click')

        self.assertTrue(os.path.exists(click))

    def test_qml_only(self):
        self.create_and_run('QML Only', 'all')
        self.assertClickExists('all')

    def test_cpp_plugin(self):
        self.create_and_run('C++', 'amd64')
        self.assertClickExists('amd64')

    def test_python(self):
        self.create_and_run('Python', 'all')
        self.assertClickExists('all')

    def test_html(self):
        self.create_and_run('HTML', 'all')
        self.assertClickExists('all')

    """
    TODO fix this test

    def test_go(self):
        self.create_and_run('Go', 'amd64')
        self.assertClickExists('amd64')
    """

    def test_rust(self):
        self.create_and_run('Rust', 'amd64')
        self.assertClickExists('amd64')
