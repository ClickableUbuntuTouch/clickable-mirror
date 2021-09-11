import os
import shutil

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
                'Arch {} unsupported by rust template'.format(self.config.build_arch))
        return rust_arch_target_mapping[self.config.build_arch]

    def build(self):
        cargo_command = 'cargo install --target {} --target-dir {} --root {} --path {}'.format(
            self._cargo_target, self.config.build_dir, self.config.install_dir, self.config.src_dir)

        if self.debug_build:
            cargo_command = '{} {}'.format(cargo_command, "--debug")
        if os.path.isdir(self.config.install_dir):
            shutil.rmtree(self.config.install_dir)


        if self.config.build_args:
            cargo_command = '{} {}'.format(cargo_command, ' '.join(self.config.build_args))

        self.container.run_command(cargo_command, use_build_dir=False, cwd=self.config.src_dir)
