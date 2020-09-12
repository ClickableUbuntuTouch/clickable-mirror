import os

from .base import Command
from clickable.exceptions import ClickableException
from clickable.logger import logger

from clickable.utils import (
    run_subprocess_check_call,
)

gdb_arch_target_mapping = {
    'amd64': 'i386:x86-64',
    'armhf': 'arm',
    'arm64': 'aarch64',
}

class GdbCommand(Command):
    def __init__(self):
        super().__init__()
        self.cli_conf.name = 'gdb'
        self.cli_conf.help_msg = 'Connects to a remote gdb session on the device opened via the gdbserver command'

        self.port = 3333
        self.binary = None

    def setup_parser(self, parser):
        parser.add_argument(
            '--port',
            default=self.port,
            help='Connect to the local GDB Server at specified port'
        )
        parser.add_argument(
            'binary',
            nargs='?',
            help='Binary to be debugged (Clickable tries to find the correct path if omitted)'
        )

    def configure(self, args):
        self.port = args.port
        self.binary = args.binary

    def is_elf_file(self, path):
        try:
            run_subprocess_check_call("readelf {} -l > /dev/null 2>&1".format(path), shell=True)
            return True
        except:
            return False

    def choose_executable(self, dirs, filename):
        for d in dirs:
            path = os.path.join(d, filename)
            if os.path.isfile(path) and os.access(path, os.X_OK):
                return path
        return None

    def find_binary_path(self):
        desktop = self.config.install_files.get_desktop(self.config.install_dir)
        exec_list = desktop["Exec"].split()
        binary = None

        for arg in exec_list:
            if "=" not in arg:
                binary = arg
                break

        path = self.choose_executable(
                [self.config.install_dir, self.config.app_bin_dir], binary)
        if path:
            if self.is_elf_file(path):
                logger.info('Going to debug "{}".'.format(path))
                return path
            else:
                raise ClickableException('App executable "{}" is not an ELF file suitable for GDB debugging.'.format(path))

        if binary == "qmlscene":
            raise ClickableException('Apps started via "qmlscene" are not supported by this debug method.')
        else:
            raise ClickableException('App binary "{}" found in desktop file could not be found in the app install directory. Please specify the path as "clickable gdb path/to/binary"'.format(binary))

    def start_gdb(self):
        libs = self.config.app_lib_dir
        arch = gdb_arch_target_mapping[self.config.arch]
        sysroot = "/usr/lib/debug/lib/{}".format(self.config.arch_triplet)
        src_dirs = [lib.src_dir for lib in self.config.lib_configs]
        src_dirs.append(self.config.root_dir)
        src_dirs = ':'.join(src_dirs)

        command = "gdb-multiarch {} -ex 'set directories {}' -ex 'set solib-search-path {}' -ex 'set architecture {}' -ex 'handle SIGILL nostop' -ex 'set sysroot {}' -ex 'target remote localhost:{}'".format(
                self.binary, src_dirs, libs, arch, sysroot, self.port)
        self.container.run_command(command, localhost=True, tty=True,
                use_build_dir=False)

    def run(self):
        if not self.binary:
            self.binary = self.find_binary_path()

        self.binary = os.path.abspath(self.binary)

        self.container.setup()
        self.start_gdb()
