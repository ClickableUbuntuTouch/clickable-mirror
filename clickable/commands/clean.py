import os
import shutil

from clickable.logger import logger
from clickable.exceptions import ClickableException
from clickable.config.constants import Constants

from .base import Command


class CleanCommand(Command):
    def __init__(self, libs=None, app=True):
        super().__init__()
        self.cli_conf.name = 'clean'
        self.cli_conf.help_msg = 'Clean the build directory'

        self.libs = libs
        self.app = app
        self.app_cache = False
        self.app_config = False
        self.app_data = False
        self.desktop_home = False
        self.go_path = False
        self.cargo_cache = False
        self.clickable_dir = False

    def setup_parser(self, parser):
        parser.add_argument(
            '--app',
            action='store_true',
            help='Clean app build dir (default when nothing else specified)',
            default=False,
        )
        parser.add_argument(
            '--libs',
            nargs='*',
            help='Clean build dir of specified libs or all libs if none is specified',
            default=None,
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Clean all build dirs (equivalent to --libs --app)',
            default=False,
        )
        parser.add_argument(
            '--app-cache',
            action='store_true',
            help='Clean app cache from Desktop Mode',
            default=False,
        )
        parser.add_argument(
            '--app-config',
            action='store_true',
            help='Clean app config from Desktop Mode',
            default=False,
        )
        parser.add_argument(
            '--app-data',
            action='store_true',
            help='Clean app data from Desktop Mode',
            default=False,
        )
        parser.add_argument(
            '--app-dirs',
            action='store_true',
            help='Combine --app-data, --app-config and --app-cache',
            default=False,
        )
        parser.add_argument(
            '--desktop-home',
            action='store_true',
            help='Clean complete Desktop Mode /home/phablet directory',
            default=False,
        )
        parser.add_argument(
            '--go-path',
            action='store_true',
            help='Clean GOPATH',
            default=False,
        )
        parser.add_argument(
            '--cargo-cache',
            action='store_true',
            help='Clean cargo cache',
            default=False,
        )
        parser.add_argument(
            '--clickable-dir',
            action='store_true',
            help='Clean Clickable directory containing Clickable config, \
                    GOPATH, cargo cache and other Clickable related data. \
                    This is like a Clickable factory reset, except for the \
                    project specific data',
            default=False,
        )

    def configure(self, args):
        default = args.libs is None
        (self.app_cache, default) = is_set(args.app_cache, default)
        (self.app_config, default) = is_set(args.app_config, default)
        (self.app_data, default) = is_set(args.app_data, default)
        (self.desktop_home, default) = is_set(args.desktop_home, default)
        (self.go_path, default) = is_set(args.go_path, default)
        (self.cargo_cache, default) = is_set(args.cargo_cache, default)
        (self.clickable_dir, default) = is_set(args.clickable_dir, default)

        if args.app_dirs:
            self.app_cache = True
            self.app_config = True
            self.app_data = True
            default = False

        self.app = args.app or args.all or default
        self.libs = [] if args.all else args.libs

        if self.libs is not None:
            existing_libs = [lib.name for lib in self.config.lib_configs]
            for lib in self.libs:
                if lib not in existing_libs:
                    raise ClickableException(
                        f'Cannot clean unknown library "{lib}", which is not in your '
                        'project config'
                    )

    def run(self):
        if self.libs is not None:
            self.clean_libs()
        if self.app:
            self.clean_app()
        if self.app_cache or self.app_config or self.app_data:
            self.clean_app_dirs()
        if self.desktop_home:
            logger.info("Cleaning Desktop Mode home directory")
            clean(Constants.desktop_device_home)
        if self.go_path:
            logger.info("Cleaning GOPATH")
            for path in self.config.gopath.split(':'):
                clean(path)
        if self.cargo_cache:
            logger.info("Cleaning cargo cache")
            clean(self.config.cargo_home)
        if self.clickable_dir:
            logger.info("Cleaning Clickable directory")
            clean(Constants.clickable_dir)

    def clean_libs(self):
        if not self.config.lib_configs:
            logger.warning('No libraries defined.')
            return

        filter_libs = self.libs

        for lib in self.config.lib_configs:
            if lib.name in filter_libs or not filter_libs:
                logger.info("Cleaning %s build directory", lib.name)
                clean(lib.build_dir)

    def clean_app(self):
        logger.info("Cleaning app build directory")
        clean(self.config.build_dir)

    def clean_app_dirs(self):
        package_name = self.config.install_files.find_package_name()
        if self.app_cache:
            logger.info("Cleaning Desktop Mode app cache")
            clean(os.path.join(Constants.desktop_device_home, '.cache', package_name))
        if self.app_config:
            logger.info("Cleaning Desktop Mode app config")
            clean(os.path.join(Constants.desktop_device_home, '.config', package_name))
        if self.app_data:
            logger.info("Cleaning Desktop Mode app data")
            clean(os.path.join(Constants.desktop_device_home, '.local', 'share', package_name))


def is_set(val, default):
    return (val, default and not val)


def clean(path):
    if os.path.exists(path):
        logger.info("  Deleting directory %s", path)
        shutil.rmtree(path)
    else:
        logger.info("  Nothing to clean, %s doesn't exist", path)
