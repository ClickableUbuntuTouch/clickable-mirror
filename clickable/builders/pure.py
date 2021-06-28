import shutil
import os
import fnmatch

from clickable.logger import logger
from clickable.config.constants import Constants

from .base import Builder
from .cmake import CMakeBuilder
from .qmake import QMakeBuilder


class PureQMLQMakeBuilder(QMakeBuilder):
    name = Constants.PURE_QML_QMAKE


class PureQMLCMakeBuilder(CMakeBuilder):
    name = Constants.PURE_QML_CMAKE


class PureBuilder(Builder):
    name = Constants.PURE

    def matches_ignore_list(self, path):
        for pattern in self.config.ignore:
            if fnmatch.fnmatch(path, pattern):
                return True
        return False

    def ignore(self, path, contents):
        ignored = []
        for content in contents:
            cpath = os.path.abspath(os.path.join(path, content))

            if (
                cpath == os.path.abspath(self.config.install_dir) or
                cpath == os.path.abspath(self.config.build_dir) or
                self.matches_ignore_list(content) or
                content in Constants.project_config_path_options
            ):
                ignored.append(content)

        return ignored

    def build(self):
        if os.path.isdir(self.config.install_dir):
            shutil.rmtree(self.config.install_dir)
        shutil.copytree(self.config.cwd, self.config.install_dir, ignore=self.ignore)
        logger.info('Copied files to install directory for click building')


class PrecompiledBuilder(PureBuilder):
    # The only difference between this and PureBuilder is that this doesn't force the "all" arch
    name = Constants.PRECOMPILED
