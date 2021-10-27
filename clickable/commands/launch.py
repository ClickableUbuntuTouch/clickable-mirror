from clickable.logger import logger

from .base import Command


class LaunchCommand(Command):
    def __init__(self):
        super().__init__()
        self.cli_conf.name = 'launch'
        self.cli_conf.help_msg = 'Launches the app on a device'

        self.package = None
        self.skip_kill = False
        self.kill = None

    def setup_parser(self, parser):
        parser.add_argument(
            'package',
            nargs='?',
            help='Full click package name to be started '
            '(defaults to the one created by Clickable)'
        )
        parser.add_argument(
            '--skip-kill',
            action='store_true',
            help='Skip killing the app before trying to start it again'
        )
        parser.add_argument(
            '--kill',
            help='Command to kill (defaults to the "kill" field defined in the '
                 'project configuration)'
        )

    def configure(self, args):
        self.package = args.package
        self.kill = args.kill
        self.skip_kill = args.skip_kill

        self.configure_common()

    def configure_nested(self):
        self.configure_common()

    def configure_common(self):
        if not self.kill:
            self.kill = self.config.kill

    def try_kill(self):
        logger.info("Trying to kill the app before starting")
        try:
            # Enclose first character in square brackets to prevent
            # spurious error when running `pkill -f` over `adb`
            kill = '[' + self.kill[:1] + ']' + self.kill[1:]
            self.device.run_command(f'pkill -f \\"{kill}\\"')
        except Exception:  # pylint: disable=broad-except
            logger.warning("Could not kill app. Maybe the device is not accessible "
                           "or the app wasn't running.")

    def run(self):
        if self.skip_kill or not self.kill:
            logger.info("Skipping kill pre-step.")
        else:
            self.try_kill()

        cwd = '.'
        if not self.package:
            self.package = self.config.install_files.find_full_package_name()
            cwd = self.config.build_dir

        launch = f'ubuntu-app-launch {self.package}'
        if self.config.launch:
            launch = self.config.launch

        logger.info("Launching app.")
        self.device.run_command(f'sleep 1s && {launch}', cwd=cwd)
