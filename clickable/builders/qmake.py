from clickable.config.constants import Constants

from .make import MakeBuilder


class QMakeBuilder(MakeBuilder):
    name = Constants.QMAKE

    def make_install(self):
        self.container.run_command(f'make INSTALL_ROOT={self.config.install_dir}/ install')

    def build(self):
        if (
            self.config.arch == Constants.host_arch or
            self.config.qt_version == "5.9" or
            self.config.arch == "all"
        ):
            command = 'qmake'
        else:
            command = f'/usr/lib/{self.config.arch_triplet}/qt5/bin/qmake'

        if self.config.build_args:
            joined_build_args = ' '.join(self.config.build_args)
            command = f'{command} {joined_build_args}'

        if self.debug_build:
            command = f'{command} CONFIG+=debug'

        # user may have defined a specific .pro file, so qmake must not read others (if any)
        if not any(arg.endswith(".pro") for arg in self.config.build_args):
            command = f'{command} {self.config.src_dir}'

        self.container.run_command(command)

        super().build()
