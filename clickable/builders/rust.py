import os
import glob
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
        if os.path.isdir(self.config.install_dir):
            shutil.rmtree(self.config.install_dir)

        # Build using cargo
        cargo_command = 'cargo build {} --target {} --target-dir {}' \
            .format('--release' if not self.debug_build else '',
                    self._cargo_target, self.config.build_dir)

        if self.config.build_args:
            cargo_command = '{} {}'.format(cargo_command, ' '.join(self.config.build_args))

        self.container.run_command(cargo_command)

        # There could be more than one executable
        executables = glob.glob(os.path.join(
            self.config.build_dir,
            self._cargo_target,
            'debug' if self.debug_build else 'release',
            "*"))
        for filename in filter(lambda f: os.path.isfile(f), executables):
            self.config.install_bin.append(filename)
