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
            joined_make_args = ' '.join(self.config.make_args)
            command = f'{command} {joined_make_args}'

        if self.config.verbose:
            command = f'{command} VERBOSE=1'

        self.container.run_command(command)

    def make_install(self):
        raise NotImplementedError('make install is not yet implemented on this builder')

    def build(self):
        self.make()
        self.post_make()
        self.make_install()
        self.post_make_install()
