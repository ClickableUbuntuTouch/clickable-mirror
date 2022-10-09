from clickable.config.constants import Constants

from .base import Builder


class QBSBuilder(Builder):
    name = Constants.QBS

    def build(self):
        command = [
            'qbs',
            'install',
            '--build-directory', self.config.build_dir,
            '--install-root', self.config.install_dir,
            'qbs.installPrefix:.',
        ]

        if self.config.verbose:
            # QBS verbose mode is a bit too verbose, let's just tell it to show the commands being
            # executed:
            command += ['--command-echo-mode', 'command-line']

        if self.debug_build:
            command.append('config:debug')
        else:
            command.append('config:release')

        if self.config.build_args:
            command += self.config.build_args

        # user may have defined a specific .qbs file, so qbs must not read others (if any)
        if not any(arg.endswith(".qbs") for arg in self.config.build_args):
            command += ['-f', self.config.src_dir]

        self.container.run_command(' '.join(command))
