from clickable.config.constants import Constants
from clickable.exceptions import ClickableException

from .base import Builder


rust_arch_target_mapping = {
    'amd64': 'x86_64-unknown-linux-gnu',
    'armhf': 'armv7-unknown-linux-gnueabihf',
    'arm64': 'aarch64-unknown-linux-gnu',
}


class RustBuilder(Builder):
    name = Constants.RUST

    @property
    def _cargo_target(self):
        if self.config.build_arch not in rust_arch_target_mapping:
            raise ClickableException(
                f'Arch {self.config.build_arch} unsupported by rust template')
        return rust_arch_target_mapping[self.config.build_arch]

    def build(self):
        cargo_command = f'cargo install --target {self._cargo_target} --target-dir ' \
                        f'{self.config.build_dir} --root {self.config.install_dir} ' \
                        f'--path {self.config.src_dir}'

        if self.debug_build:
            cargo_command = f'{cargo_command} --debug'

        if self.config.verbose:
            cargo_command = f'{cargo_command} --verbose'

        if self.config.build_args:
            joined_build_args = ' '.join(self.config.build_args)
            cargo_command = f'{cargo_command} {joined_build_args}'

        self.container.run_command(cargo_command, use_build_dir=False, cwd=self.config.src_dir)
