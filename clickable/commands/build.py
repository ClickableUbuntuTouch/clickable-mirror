import os
import sys
import shutil

from clickable.utils import (
    get_builder,
    makedirs,
    is_sub_dir,
    env,
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

        self.clean_app = False
        self.clean_libs = False
        self.output_path = None
        self.skip_review = skip_review or skip_click
        self.skip_click = skip_click
        self.debug_build = False
        self.app = True
        self.libs = None

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
            help='Do not review click package after build (useful for unconfined apps)',
            default=False,
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
        self.clean_app = args.clean
        self.clean_libs = args.clean and args.libs is not None
        if args.skip_review:
            self.skip_review = True
        self.output_path = args.output
        self.debug_build = args.debug
        self.app = args.app or args.libs is None or args.all
        self.libs = [] if args.all else args.libs

        self.configure_common()

    def configure_nested(self):
        self.configure_common()

    def configure_common(self):
        if self.config.global_config.build.skip_review:
            self.skip_review = True

        if self.config.always_clean or self.config.global_config.build.always_clean:
            self.clean_app = True

        self.parse_env()
        self.check_libs()

    def parse_env(self):
        if env('CLICKABLE_DEBUG_BUILD'):
            self.debug_build = True
            self.config.debug_build = True
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

    def run(self):
        if self.libs is not None:
            self.build_libs()
        if self.app:
            self.build_app()

    def build_libs(self):
        if not self.config.lib_configs:
            logger.warning('No libraries defined.')
            return

        if self.clean_libs:
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
        if self.clean_app:
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
            review.check(self.click_path, raise_on_error=False)

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
            self.run_custom_commands(config.prebuild)

        run_builder(config, container, self.debug_build)

        if is_app:
            self.install_additional_files()

        if config.postbuild:
            self.run_custom_commands(config.postbuild)

    def install_files(self, pattern, dest_dir):
        if not is_sub_dir(dest_dir, self.config.install_dir):
            dest_dir = os.path.abspath(self.config.install_dir + "/" + dest_dir)

        makedirs(dest_dir)
        if '"' in pattern:
            # Make sure one cannot run random bash code through the "ls" command
            raise ClickableException(
                "install_* patterns must not contain any '\"' quotation character."
            )

        command = f'ls -d "{pattern}"'
        files = self.container.run_command(command, get_output=True).split()

        logger.info("Installing %s", ", ".join(files))
        self.container.pull_files(files, dest_dir)

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

            if module:
                self.install_files(pattern, os.path.join(
                    dest_dir, *module.split('.')[:-1])
                )
            else:
                self.install_files(pattern, dest_dir)

    def install_additional_files(self):
        for p in self.config.install_root_data:
            self.install_files(p, self.config.install_dir)
        for p in self.config.install_lib:
            self.install_files(p, os.path.join(self.config.install_dir,
                                               self.config.app_lib_dir))
        for p in self.config.install_bin:
            self.install_files(p, os.path.join(self.config.install_dir,
                                               self.config.app_bin_dir))
        for p in self.config.install_qml:
            self.install_qml_files(p, os.path.join(
                self.config.install_dir,
                self.config.app_qml_dir
            ))
        for p, dest in self.config.install_data.items():
            self.install_files(p, dest)

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
            logger.warning('Framework in manifest is "%s", Clickable expected "%s".',
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

    def run_custom_commands(self, commands):
        if commands:
            for cmd in commands:
                self.container.run_command(cmd, cwd=self.config.cwd)


def run_builder(config, container, debug_build):
    builder = get_builder(config, container, debug_build)
    builder.build()
