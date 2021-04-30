from clickable.utils import run_subprocess_check_call

from .base import Command


class ScreenshotsCommand(Command):
    def __init__(self):
        super().__init__()
        self.cli_conf.name = 'screenshots'
        self.cli_conf.help_msg = 'Download all the screenshots from the device'

    def run(self):
        command = 'adb pull /home/phablet/Pictures/Screenshots'
        run_subprocess_check_call(command, cwd=self.config.cwd)
