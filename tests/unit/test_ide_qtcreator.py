from clickable.config.constants import Constants
import os
import shutil
from clickable.commands.docker.docker_config import DockerConfig
from clickable.commands.idedelegates.qtcreator import QtCreatorDelegate

from .base_test import UnitTest
from unittest import mock
from ..mocks import true_fn


class TestIdeQtCreatorCommand(UnitTest):

    def setUp(self):
        super().setUp()
        self.setUpConfig()
        self.docker_config = DockerConfig()
        self.docker_config.add_environment_variables(
            {
                "LD_LIBRARY_PATH": "/usr/bin",
                "CLICK_LD_LIBRARY_PATH": "/tmp/fake/qmlproject/build/app/install",
                "QML2_IMPORT_PATH": "/tmp/qmllibs",
                "CLICK_QML2_IMPORT_PATH": "/tmp/fake/qmlproject/build/app/install",
                "CLICK_PATH": "/tmp/fake/qmlproject/build/app/install/lib",
                "PATH": "/usr/bin"
            }
        )

        self.idedelegate = QtCreatorDelegate(self.config)
        Constants.clickable_dir = '/tmp/tests/.clickable'
        self.idedelegate.project_path = '/tmp/tests/qmlproject'
        self.output_file = os.path.join(
            self.idedelegate.project_path,
            'CMakeLists.txt.user.shared'
        )

        self.idedelegate.target_settings_path = os.path.join(
            Constants.clickable_dir,
            'QtProject'
        )

        os.makedirs(self.idedelegate.project_path)

    def test_command_overrided(self):

        # project path should not be added to qtcreator command if not a cmake/qmake/qbs project
        path_arg = self.idedelegate.override_command('qtcreator')
        self.assertEqual(
            path_arg,
            'qtcreator -settingspath {} '.format(Constants.clickable_dir)
        )

        # supported projects
        expected_path = 'qtcreator -settingspath {} {}'.format(
            Constants.clickable_dir,
            self.idedelegate.project_path
        )

        # cmake project
        open(os.path.join(self.idedelegate.project_path, 'CMakeLists.txt'), 'a').close()
        path_arg = self.idedelegate.override_command('qtcreator')
        self.assertEqual(path_arg, expected_path)
        os.remove(os.path.join(self.idedelegate.project_path, 'CMakeLists.txt'))

        # qmake
        open(os.path.join(self.idedelegate.project_path, 'fakeProject.pro'), 'a').close()
        path_arg = self.idedelegate.override_command('qtcreator')
        self.assertEqual(path_arg, expected_path)
        os.remove(os.path.join(self.idedelegate.project_path, 'fakeProject.pro'))

        # qbs
        open(os.path.join(self.idedelegate.project_path, 'fakeProject.qbs'), 'a').close()
        path_arg = self.idedelegate.override_command('qtcreator')
        self.assertEqual(path_arg, expected_path)
        os.remove(os.path.join(self.idedelegate.project_path, 'fakeProject.qbs'))

    def test_initialize_qtcreator_conf(self):

        self.idedelegate.before_run(None, self.docker_config)
        self.assertTrue(os.path.isdir('/tmp/tests/.clickable/QtProject'))

    @mock.patch('clickable.commands.idedelegates.qtcreator.QtCreatorDelegate.init_cmake_project',
                side_effect=true_fn)
    def test_project_pre_configured(self, mock_init_cmake_project):

        # no cmake file
        self.idedelegate.before_run(None, self.docker_config)
        mock_init_cmake_project.assert_not_called()

        # project already configured
        open(os.path.join(self.idedelegate.project_path, 'CMakeLists.txt.user.shared'),
             'a').close()
        self.idedelegate.before_run(None, self.docker_config)
        mock_init_cmake_project.assert_not_called()
        os.remove(os.path.join(self.idedelegate.project_path, 'CMakeLists.txt.user.shared'))

        # if not a cmake builder, must not be called
        for builder in [Constants.QBS, Constants.QMAKE, Constants.PURE_QML_QMAKE, Constants.RUST]:
            self.config.builder = builder
            self.idedelegate.before_run(None, self.docker_config)
            mock_init_cmake_project.assert_not_called()

        # now should try to pre-configure only if the project is a cmake project
        self.config.builder = Constants.CMAKE
        open(os.path.join(self.idedelegate.project_path, 'CMakeLists.txt'), 'a').close()
        self.idedelegate.before_run(None, self.docker_config)
        mock_init_cmake_project.assert_called()

    def test_recurse_replace(self):

        final_command = self.idedelegate.recurse_replace('qmlscene --ok=\"args\"', {})
        assert 'qmlscene --ok=\"args\"' == final_command

        final_command = self.idedelegate.recurse_replace('\"qmlscene --ok=\"args\"\"', {})
        assert '\"qmlscene --ok=\"args\"\"' == final_command

        cmake_vars = {
            'FAKE': 'qmlscene'
        }
        final_command = self.idedelegate.recurse_replace('${FAKE} --ok=\"args\"', cmake_vars)
        assert 'qmlscene --ok=\"args\"' == final_command

        # test with recursive vars
        cmake_vars = {
            'FAKE_SUBVAR': 'share/foo',
            'FAKE_VAR': '${FAKE_SUBVAR}/hello'
        }
        final_command = self.idedelegate.recurse_replace('${FAKE_VAR} --args someargs', cmake_vars)
        assert 'share/foo/hello --args someargs' == final_command

    @mock.patch('clickable.config.file_helpers.ProjectFiles.find_any_executable', return_value='')
    @mock.patch('clickable.config.file_helpers.ProjectFiles.find_any_exec_args')
    def test_init_cmake_project_no_exe(self, find_any_executable_mock, find_any_exec_args_mock):

        # if Exec not found in desktop, should do nothing
        self.idedelegate.init_cmake_project(self.config, self.docker_config)
        self.assertFalse(os.path.isfile(self.output_file))

    @mock.patch(
        'clickable.config.file_helpers.ProjectFiles.find_any_executable',
        return_value='fake_exe'
    )
    @mock.patch('clickable.config.file_helpers.ProjectFiles.find_any_exec_args')
    def test_init_cmake_project_no_to_prompt(
            self,
            find_any_executable_mock,
            find_any_exec_args_mock
    ):
        # mock prompt
        original_input = mock.builtins.input
        mock.builtins.input = lambda _: "no"
        self.idedelegate.config.interactive = True

        # user choose not to let clickable generate config
        self.idedelegate.init_cmake_project(self.config, self.docker_config)
        self.assertFalse(os.path.isfile(self.output_file))

        mock.builtins.input = original_input

    @mock.patch(
        'clickable.config.file_helpers.ProjectFiles.find_any_executable',
        return_value='fake_exe'
    )
    @mock.patch('clickable.config.file_helpers.ProjectFiles.find_any_exec_args', return_value=[])
    def test_init_cmake_project(self, find_any_executable_mock, find_any_exec_args_mock):
        # mock prompt
        original_input = mock.builtins.input
        mock.builtins.input = lambda _: "yes"
        self.idedelegate.config.interactive = True

        # now he is ok to let clickable build the configuration template
        self.idedelegate.init_cmake_project(self.config, self.docker_config)
        self.assertTrue(os.path.isfile(self.output_file))
        # test an example variable that have been replaced
        self.assertTrue(
            open(self.output_file, 'r').read().find(
                'CustomExecutableRunConfiguration.Arguments">fake_exe</value>'
            )
        )

        mock.builtins.input = original_input

    @mock.patch(
        'clickable.config.file_helpers.ProjectFiles.find_any_executable',
        return_value='@FAKE_EXE@'
    )
    @mock.patch('clickable.config.file_helpers.ProjectFiles.find_any_exec_args', return_value=[])
    def test_init_cmake_project_exe_as_var(
            self,
            find_any_executable_mock,
            find_any_exec_args_mock
    ):
        # Exec command as variable
        cmake_file = open(os.path.join(self.idedelegate.project_path, 'CMakeLists.txt'), 'w')
        cmake_file.write("set(FAKE_EXE \"qmlscene --ok=\"args\"\")")
        cmake_file.close()

        self.idedelegate.init_cmake_project(self.config, self.docker_config)
        # test that final exe var is found
        generated_shared_file = open(self.output_file, 'r').read()
        self.assertTrue(generated_shared_file.find(
            'CustomExecutableRunConfiguration.Arguments">qmlscene</value>'
        ))
        self.assertTrue(generated_shared_file.find(
            'CustomExecutableRunConfiguration.Arguments">--ok="args"</value>'
        ))

    def tearDown(self):
        shutil.rmtree(self.idedelegate.project_path, ignore_errors=True)
