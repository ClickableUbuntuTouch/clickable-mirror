import re

from clickable.config.constants import Constants
from clickable.logger import logger

from .make import MakeBuilder

BUILD_TYPE = 'CMAKE_BUILD_TYPE'
INSTALL_PREFIX = 'CMAKE_INSTALL_PREFIX'


class CMakeBuilder(MakeBuilder):
    name = Constants.CMAKE

    def make_install(self):
        self.container.run_command(f'make DESTDIR={self.config.install_dir}/ install')

    def build(self):
        command = ['cmake']

        if self.debug_build:
            logger.info('Setting CMake build type to "Debug"')

            self.config.build_args = remove_arg(self.config.build_args, BUILD_TYPE)
            self.config.build_args.append(f'-D{BUILD_TYPE}=Debug')
        elif not has_arg(self.config.build_args, BUILD_TYPE):
            logger.debug('Defaulting CMake build type to "Release"')

            self.config.build_args.append(f'-D{BUILD_TYPE}=Release')

        if not has_arg(self.config.build_args, INSTALL_PREFIX):
            self.config.build_args.append(f'-D{INSTALL_PREFIX}:PATH=/.')

        command += self.config.build_args
        command.append(self.config.src_dir)

        self.container.run_command(" ".join(command))

        super().build()


def has_arg(args, name):
    pattern = get_arg_pattern(name)
    return any(pattern.match(a) for a in args)


def remove_arg(args, name):
    pattern = get_arg_pattern(name)
    return [a for a in args if not pattern.match(a)]


def get_arg_pattern(name):
    return re.compile(r'-D\s*' + name + r'(:\w+)?=')
