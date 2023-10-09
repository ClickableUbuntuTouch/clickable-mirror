import os
import sys
import shutil
from clickable.config.constants import Constants

from clickable.utils import (
    get_builder,
    makedirs,
    is_sub_dir,
    env,
    make_absolute,
)
from clickable.container import Container
from clickable.logger import logger
from clickable.exceptions import ClickableException

from .base import Command
from .review import ReviewCommand
from .clean import CleanCommand


class BuildCommand(Command):
    click_path = ''

    def __init__(self, skip_review=False, skip_click=False):
        super().__init__()
        self.cli_conf.name = 'build'
        self.cli_conf.help_msg = 'Build the app and/or libraries'
        self.command_conf.build_command = True

        self.clean = False
        self.output_path = None
        self.skip_review = skip_review or skip_click
        self.skip_click = skip_click
        self.debug_build = False
        self.app = True
        self.libs = None
        self.accept_errors = False
        self.accept_warnings = False

    def setup_parser(self, parser):
        parser.add_argument(
            '--clean',
            action='store_true',
            help='Clean build directory before building (only applies for app)',
            default=False,
        )
        parser.add_argument(
            '--output',
            help='Where to output the compiled click package',
        )
        parser.add_argument(
            '--debug',
            action='store_true',
            help='Perform a debug build',
            default=False,
        )
        parser.add_argument(
            '--skip-review',
            action='store_true',
            help='Do not review click package after build',
            default=False,
        )
        parser.add_argument(
            '--accept-review-warnings',
            action='store_true',
            help='Return with exit-code 0 even when there are review warnings'
        )
        parser.add_argument(
            '--accept-review-errors',
            action='store_true',
            help='Return with exit-code 0 even when there are review errors '
            '(implies --accept-review-warnings)'
        )
        parser.add_argument(
            '--app',
            action='store_true',
            help='Build app after building libs (only needed when using --libs as well)',
            default=False,
        )
        parser.add_argument(
            '--libs',
            nargs='*',
            help='Build specified libs or all libs if none is specified',
            default=None,
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Build libraries and app (equivalent to --libs --app)',
            default=False,
        )

    def configure(self, args):
        self.clean = args.clean
        if args.skip_review:
            self.skip_review = True
        self.output_path = args.output
        self.debug_build = args.debug
        self.app = args.app or args.libs is None or args.all
        self.libs = [] if args.all else args.libs

        self.configure_common()

        if args.accept_review_warnings:
            self.accept_warnings = True

        if args.accept_review_errors:
            self.accept_errors = True

        if self.accept_errors:
            self.accept_warnings = True

    def configure_nested(self):
        self.configure_common()

        if self.accept_errors:
            self.accept_warnings = True

    def configure_common(self):
        if self.config.skip_review or self.config.global_config.build.skip_review:
            self.skip_review = True

        if self.config.always_clean or self.config.global_config.build.always_clean:
            self.clean = True

        if self.config.ignore_review_errors is not None:
            self.accept_errors = self.config.ignore_review_errors

        if self.config.ignore_review_warnings is not None:
            self.accept_warnings = self.config.ignore_review_warnings

        self.parse_env()
        self.check_libs()

    def parse_env(self):
        if env('CLICKABLE_DEBUG_BUILD'):
            self.debug_build = True
            self.config.env_vars['DEBUG_BUILD'] = '1'

            for lib in self.config.lib_configs:
                lib.env_vars['DEBUG_BUILD'] = '1'

        if not self.output_path:
            output_env = env('CLICKABLE_OUTPUT')
            if output_env:
                self.output_path = output_env

    def check_libs(self):
        if self.libs is not None:
            existing_libs = [lib.name for lib in self.config.lib_configs]
            for lib in self.libs:
                if lib not in existing_libs:
                    raise ClickableException(
                        f'Cannot build unknown library "{lib}", which is not in your '
                        'project config'
                    )

                for config in self.config.lib_configs:
                    if lib == config.name:
                        if config.restrict_arch and config.restrict_arch != config.arch:
                            raise ClickableException(
                                f'Cannot build library {config.name} for architecture '
                                f'"{config.arch}" as it is restricted '
                                f'to "{config.restrict_arch}" in the project config.'
                            )

    def run(self):
        if self.libs is not None:
            self.build_libs()
        if self.app:
            self.build_app()

    def build_libs(self):
        if not self.config.lib_configs:
            logger.warning('No libraries defined.')
            return

        if self.clean:
            clean_cmd = CleanCommand(libs=self.libs, app=False)
            clean_cmd.init_from_command(self)
            clean_cmd.run()

        filter_libs = self.libs

        for lib in self.config.lib_configs:
            if lib.name in filter_libs or not filter_libs:
                logger.info("Building %s", lib.name)

                container = Container(lib, lib.name)

                # This is a workaround for lib env vars being overwritten by
                # project env vars, especially affecting Container Mode.
                lib.set_env_vars()

                self.build(lib, container, is_app=False)

    def build_app(self):
        self.create_lib_build_warning()

        if self.clean:
            clean_cmd = CleanCommand()
            clean_cmd.init_from_command(self)
            clean_cmd.run()

        logger.info("Building app")
        self.build(self.config, self.container)

        if not self.skip_click:
            self.click_build()

        if not self.skip_review:
            review = ReviewCommand()
            review.init_from_command(self)
            review.check(
                self.click_path,
                raise_on_error=not self.accept_errors,
                raise_on_warning=not self.accept_warnings)

    def build(self, config, container, is_app=True):
        try:
            makedirs(config.build_dir)
        except Exception:  # pylint: disable=broad-except
            logger.warning(
                'Failed to create the build directory: %s', str(sys.exc_info()[0])
            )

        try:
            makedirs(config.build_home)
        except Exception:  # pylint: disable=broad-except
            logger.warning(
                'Failed to create the build home directory: %s', str(sys.exc_info()[0])
            )

        if os.path.isdir(config.install_dir):
            shutil.rmtree(config.install_dir)

        try:
            makedirs(config.install_dir)
        except Exception:  # pylint: disable=broad-except
            logger.warning(
                'Failed to create the build home directory: %s', str(sys.exc_info()[0])
            )

        container.setup()

        if config.prebuild:
            run_custom_commands(config.prebuild, config, container)

        run_builder(config, container, self.debug_build)

        if is_app:
            self.install_additional_files()

        if config.postbuild:
            run_custom_commands(config.postbuild, config, container)

    def install_files(self, pattern, dest_dir, search_dirs=None, install_type=""):
        if not is_sub_dir(dest_dir, self.config.install_dir):
            dest_dir = os.path.abspath(self.config.install_dir + "/" + dest_dir)

        makedirs(dest_dir)

        if "'" in pattern:
            # Make sure one cannot run random bash code through the "ls" command
            raise ClickableException(
                "install_* patterns must not contain the ' quotation character."
            )

        name = pattern
        if "/" in pattern:
            [parent, name] = make_absolute(pattern).rsplit('/', 1)
            parent += "/"
        else:
            if not search_dirs:
                search_dirs = []
            search_dirs.append(self.config.root_dir)

            # deduplicate
            search_dirs = list(set(search_dirs))
            parent = " ".join(search_dirs)

        command = f"find {parent} -name '{name}' -maxdepth 1 -mindepth 1"
        files = self.container.run_command(command, get_output=True).split()

        if not files:
            raise ClickableException(f'Files to install not found with pattern "{pattern}"')

        logger.info("Installing %s\n  %s", install_type, "\n  ".join(files))

        files_joined = " ".join(files)
        self.container.run_command(f"cp --recursive --no-dereference {files_joined} {dest_dir}")

    def install_qml_files(self, pattern, dest_dir):
        if '*' in pattern:
            self.install_files(pattern, dest_dir)
        else:
            qmldir_file = os.path.join(pattern, 'qmldir')
            command = f'cat {qmldir_file}'
            qmldir = self.container.run_command(command, get_output=True)
            module = None
            for line in qmldir.split('\n'):
                if line.startswith('module'):
                    module = line.split(' ')[1]

            install_type = "QML modules"
            if module:
                self.install_files(pattern, os.path.join(
                    dest_dir, *module.split('.')[:-1]), install_type=install_type
                )
            else:
                self.install_files(pattern, dest_dir, install_type=install_type)

    def join_libs(self, dirs):
        lib_bin_dirs = []
        for lib in self.config.lib_configs:
            for d in dirs:
                lib_bin_dirs.append(os.path.join(lib.install_dir, d[1:]))
        return [d for d in lib_bin_dirs if os.path.isdir(d)]

    def get_library_dirs(self):
        command = "readlink -e $(cat /etc/ld.so.conf.d/*.conf) || true"
        dirs = self.container.run_command(command, get_output=True).splitlines()
        dirs += self.join_libs(dirs)

        for lib in self.config.lib_configs:
            candidate = os.path.join(lib.install_dir, "lib")
            if os.path.isdir(candidate):
                dirs.append(candidate)

        if self.config.is_foreign_target():
            dirs = [d for d in dirs if Constants.host_arch_triplet not in d]

        return list({os.path.realpath(d) for d in dirs})

    def get_bin_dirs(self):
        command = "echo ${PATH}"
        dirs = self.container.run_command(command, get_output=True).split(":")
        dirs += self.join_libs(dirs)

        return [d for d in dirs if os.path.isdir(d)]

    def install_additional_files(self):
        for p in self.config.install_root_data:
            self.install_files(p, self.config.install_dir, "root data")

        if self.config.install_lib:
            lib_dirs = self.get_library_dirs()
            for p in self.config.install_lib:
                self.install_files(p, os.path.join(self.config.install_dir,
                                                   self.config.app_lib_dir), lib_dirs, "libraries")

        if self.config.install_bin:
            bin_dirs = self.get_bin_dirs()
            for p in self.config.install_bin:
                self.install_files(p, os.path.join(self.config.install_dir,
                                                   self.config.app_bin_dir), bin_dirs, "binaries")

        for p in self.config.install_qml:
            self.install_qml_files(p, os.path.join(
                self.config.install_dir,
                self.config.app_qml_dir)
            )

        for p, dest in self.config.install_data.items():
            self.install_files(p, dest, "data")

    def set_arch(self, manifest):
        arch = manifest.get('architecture', None)

        if arch in ['@CLICK_ARCH@', '']:
            manifest['architecture'] = self.config.arch
            return True

        if arch != self.config.arch:
            raise ClickableException(
                f'Clickable is building for architecture "{self.config.arch}", but "{arch}" is '
                'specified in the manifest. You can set the architecture field to @CLICK_ARCH@ to '
                'let Clickable set the architecture field automatically.'
            )

        return False

    def set_framework(self, manifest):
        framework = manifest.get('framework', None)

        if framework in ['@CLICK_FRAMEWORK@', '']:
            manifest['framework'] = self.config.framework
            return True

        if framework != self.config.framework:
            logger.debug('Framework in manifest is "%s", Clickable expected "%s".',
                         framework, self.config.framework)

        return False

    def manipulate_manifest(self):
        manifest = self.config.install_files.get_manifest()
        has_changed = False

        if self.set_arch(manifest):
            has_changed = True

        if self.set_framework(manifest):
            has_changed = True

        if has_changed:
            self.config.install_files.write_manifest(manifest)

    def click_build(self):
        self.manipulate_manifest()

        command = f'click build {self.config.install_dir} --no-validate'
        self.container.run_command(command)

        click = self.config.install_files.get_click_filename()
        self.click_path = os.path.join(self.config.build_dir, click)

        if self.output_path:
            output_file = os.path.join(self.output_path, click)

            if not os.path.exists(self.output_path):
                makedirs(self.output_path)

            shutil.copyfile(self.click_path, output_file)
            self.click_path = output_file

        logger.debug('Click outputted to %s', self.click_path)

    def create_lib_build_warning(self):
        missing = [lib.name for lib in self.config.lib_configs
                   if not os.path.isdir(lib.build_dir)
                   and lib.arch == self.config.arch]  # lib arch might be restricted

        if missing:
            logger.warning(
                'Library build dir missing (%s). Please check the build instructions. '
                'You might need to run "clickable build --libs".',
                ", ".join(missing))


def run_custom_commands(commands, config, container):
    if commands:
        for cmd in commands:
            container.run_command(cmd, cwd=config.cwd)


def run_builder(config, container, debug_build):
    builder = get_builder(config, container, debug_build)
    builder.build()
