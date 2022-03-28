from clickable.config.constants import Constants

from .base import Builder


class GoBuilder(Builder):
    name = Constants.GO

    def build(self):
        command = [
            '/usr/local/go/bin/go',
            'build',
            '-pkgdir', self.config.build_dir,
            '-o', self.config.install_dir,
            '.',
        ]

        self.container.run_command(' '.join(command),
                                   use_build_dir=False, cwd=self.config.src_dir)
