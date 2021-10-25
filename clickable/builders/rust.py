from clickable.config.constants import Constants

from .base import Builder


class RustBuilder(Builder):
    name = Constants.RUST

    def build(self):
        channel = self.config.rust_channel
        if not channel:
            channel = '$CLICKABLE_RUST_CHANNEL'

        command = [
            'cargo',
            f'+{channel}',
            'install',
            '--target', self.config.arch_rust,
            '--target-dir', self.config.build_dir,
            '--root', self.config.install_dir,
            '--path', self.config.src_dir,
        ]

        if self.debug_build:
            command.append('--debug')

        if self.config.verbose:
            command.append('--verbose')

        if self.config.build_args:
            command += self.config.build_args

        self.container.run_command(' '.join(command),
                                   use_build_dir=False, cwd=self.config.src_dir)
