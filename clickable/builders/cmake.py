from clickable.config.constants import Constants

from .make import MakeBuilder


class CMakeBuilder(MakeBuilder):
    name = Constants.CMAKE

    def make_install(self):
        self.container.run_command(f'make DESTDIR={self.config.install_dir}/ install')

    def build(self):
        command = 'cmake'

        if self.config.build_args:
            joined_build_args = ' '.join(self.config.build_args)
            command = f'{command} {joined_build_args}'

        if self.debug_build:
            command = f'{command} -DCMAKE_BUILD_TYPE=Debug'
        else:
            command = f'{command} -DCMAKE_BUILD_TYPE=Release'

        self.container.run_command(
            f'{command} {self.config.src_dir} -DCMAKE_INSTALL_PREFIX:PATH=/.')

        super().build()
