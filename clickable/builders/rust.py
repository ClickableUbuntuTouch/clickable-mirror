from clickable.config.constants import Constants

from .base import Builder


class RustBuilder(Builder):
    name = Constants.RUST

    def build(self):
        command = self.construct_cargo_command("install")

        # cargo install appends "/bin". Choosing the app lib dir for the app and the install dir
        # for rust libraries
        install_dir = self.config.config.get("app_lib_dir", self.config.install_dir)
        command += [
            '--locked',
            '--root', install_dir,
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

    def test(self, is_app=True):
        test = self.config.test
        if not test:
            test = ' '.join(self.construct_cargo_command("test"))

        command = f'xvfb-startup {test}'
        self.container.run_command(command,
                                   use_build_dir=False, cwd=self.config.src_dir)

    def construct_cargo_command(self, command):
        channel = self.config.rust_channel
        if not channel:
            channel = '$CLICKABLE_RUST_CHANNEL'

        return [
            'cargo',
            f'+{channel}',
            command,
            '--target', self.config.arch_rust,
            '--target-dir', self.config.build_dir,
        ]
