import shutil
import os

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

    def _ignore(self, path, contents):
        ignored = []
        for content in contents:
            cpath = os.path.abspath(os.path.join(path, content))

            if (
                cpath == os.path.abspath(self.config.install_dir) or
                cpath == os.path.abspath(self.config.build_dir) or
                content in self.config.ignore or
                content == 'clickable.json'
            ):
                ignored.append(content)

        return ignored

    def build(self):
        if os.path.isdir(self.config.install_dir):
            shutil.rmtree(self.config.install_dir)
        shutil.copytree(self.config.cwd, self.config.install_dir, ignore=self._ignore)
        logger.info('Copied files to install directory for click building')


class PrecompiledBuilder(PureBuilder):
    # The only difference between this and PureBuilder is that this doesn't force the "all" arch
    name = Constants.PRECOMPILED
