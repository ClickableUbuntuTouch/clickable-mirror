import subprocess

from .base import Builder


class MakeBuilder(Builder):
    def post_make(self):
        if self.config.postmake:
            for cmd in self.config.postmake:
                subprocess.check_call(cmd, cwd=self.config.build_dir, shell=True)

    def post_make_install(self):
        pass

    def make(self):
        command = 'make'
        if self.config.make_args:
            command = '{} {}'.format(command, ' '.join(self.config.make_args))

        if self.config.verbose:
            command = '{} {}'.format(command, 'VERBOSE=1')

        self.container.run_command(command)

    def make_install(self):
        raise NotImplementedError('make install is not yet implemented on this builder')

    def build(self):
        self.make()
        self.post_make()
        self.make_install()
        self.post_make_install()
