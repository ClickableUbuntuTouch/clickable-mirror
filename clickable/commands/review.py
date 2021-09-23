import os
import subprocess

from clickable.logger import logger

from .base import Command


class ReviewCommand(Command):
    def __init__(self):
        super().__init__()
        self.cli_conf.name = 'review'
        self.cli_conf.help_msg = 'Runs click-review against click package'

        self.click = None
        self.accept_errors = False
        self.accept_warnings = False

    def setup_parser(self, parser):
        parser.add_argument(
            'click',
            nargs='?',
            help='Click package to be reviewed (defaults to the one in the build dir)'
        )
        parser.add_argument(
            '--accept-warnings',
            action='store_true',
            help='Return with exit-code 0 even when there are warnings'
        )
        parser.add_argument(
            '--accept-errors',
            action='store_true',
            help='Return with exit-code 0 even when there are errors (implies --accept-warnings)'
        )

    def configure(self, args):
        self.click = args.click
        self.accept_errors = args.accept_errors
        self.accept_warnings = self.accept_errors or args.accept_warnings

    def check(self, path=None, raise_on_error=False, raise_on_warning=False):
        if path:
            path = os.path.abspath(path)

        if path:
            click = os.path.basename(path)
            click_path = path
        else:
            click = self.config.install_files.get_click_filename()
            click_path = os.path.join(self.config.build_dir, click)

        cwd = os.path.dirname(os.path.realpath(click_path))

        try:
            logger.info("Running review on %s", click_path)
            self.container.run_command(
                f'click-review {click_path}',
                use_build_dir=False,
                cwd=cwd
            )
        except subprocess.CalledProcessError as e:
            if e.returncode == 2 and not raise_on_error:
                pass
            elif e.returncode == 3 and not raise_on_warning:
                pass
            else:
                raise e

    def run(self):
        self.check(
            path=self.click,
            raise_on_error=not self.accept_errors,
            raise_on_warning=not self.accept_warnings
        )
