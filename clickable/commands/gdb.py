import os

from .base import Command
from clickable.exceptions import ClickableException
from clickable.logger import logger
from clickable.config.constants import Constants

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
        self.cli_conf.help_msg = 'Connects to a remote gdb session on the device opened via the gdbserver command.'

        self.script = None
        self.export_script = None
        self.export_debug_symbols = None
        self.port = 3333
        self.binary = None
        self.configure_app = True
        self.add_sysroot = True
        self.forward = []
        self.debug_symbols = None

    def setup_parser(self, parser):
        parser.add_argument(
            '--script',
            help='Create a gdb script for external use instead of running gdb'
        )
        parser.add_argument(
            '--export',
            help='Export system debug symbols from docker image (most useful in combination with --script)'
        )
        parser.add_argument(
            '--port',
            default=self.port,
            help='Connect to the local GDB Server at specified port'
        )
        parser.add_argument(
            '--binary',
            help='Binary to be debugged (Clickable tries to find the correct path if omitted)'
        )
        parser.add_argument(
            '--no-app-config',
            action='store_true',
            help='Do not configure gdb with source and solib directories from the app and its libraries.'
        )
        parser.add_argument(
            '--no-sysroot',
            action='store_true',
            help='Do not configure a host side sysroot containing system libraries (be aware that this slows down app startup).'
        )
        parser.add_argument(
            'forward',
            nargs='*',
            metavar='gdb-param',
            help='Params forwarded to gdb-multiarch directly. Prepend with "--" to make sure they are not interpreted by Clickable.'
        )

    def configure(self, args):
        self.export_script = args.script
        self.export_debug_symbols = args.export
        self.port = args.port
        self.binary = args.binary
        self.configure_app = not args.no_app_config
        self.add_sysroot = not args.no_sysroot
        self.forward = args.forward

        self.configure_nested()

    def configure_nested(self):
        self.debug_symbols = "/usr/lib/debug/lib/{}".format(self.config.arch_triplet)

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
                return path
            else:
                raise ClickableException('App executable "{}" is not an ELF file suitable for GDB debugging.'.format(path))

        if binary == "qmlscene":
            raise ClickableException('Apps started via "qmlscene" are not supported by this debug method.')
        else:
            raise ClickableException('App binary "{}" found in desktop file could not be found in the app install directory. Please specify the path as "clickable gdb path/to/binary"'.format(binary))

    def create_script(self):
        self.script = []

        arch = gdb_arch_target_mapping[self.config.arch]
        self.script.append('set architecture {}'.format(arch))

        self.script.append('file {}'.format(self.binary))

        if self.configure_app:
            src_dirs = [lib.src_dir for lib in self.config.lib_configs]
            src_dirs.append(self.config.src_dir)
            src_dirs = ':'.join(src_dirs)
            self.script.append('set directories {}'.format(src_dirs))

            libs = self.config.app_lib_dir
            self.script.append('set solib-search-path {}'.format(libs))

        if self.add_sysroot:
            sysroot = self.debug_symbols

            if self.export_debug_symbols:
                sysroot = '{}/{}'.format(self.export_debug_symbols, sysroot)

            sysroot = os.path.abspath(sysroot)
            self.script.append('set sysroot {}'.format(sysroot))

        self.script.append('target remote localhost:{}'.format(self.port))

    def write_debug_symbols(self):
        logger.info("Writing debug symbols to {}".format(self.export_debug_symbols))

        dst = '{}/{}'.format(self.export_debug_symbols, os.path.dirname(self.debug_symbols))
        self.container.pull_files([self.debug_symbols], dst)

    def write_script(self):
        logger.info("Writing GDB init script to {0}. Run it from a multiarch GDB shell via 'source {0}'.".format(
            self.export_script))

        with open(self.export_script, 'w') as script_file:
            for command in self.script:
                script_file.write(command)
                script_file.write('\n')

    def start_gdb(self):
        args = ["-ex '{}'".format(cmd) for cmd in self.script]
        args += self.forward
        command = 'gdb-multiarch {}'.format(' '.join(args))

        logger.info('Starting GDB for "{}".'.format(self.binary))
        self.container.run_command(command, localhost=True,
                tty=self.config.interactive, use_build_dir=False)

    def run(self):
        if not self.binary:
            self.binary = self.find_binary_path()
        self.binary = os.path.abspath(self.binary)

        self.create_script()

        run_gdb = not self.export_script and not self.export_debug_symbols
        
        if run_gdb or self.export_debug_symbols:
            self.container.setup()

        if self.export_debug_symbols:
            self.write_debug_symbols()

        if self.export_script:
            self.write_script()

        if run_gdb:
            self.start_gdb()
