import os

from .utils import (
    run_subprocess_check_output,
    run_subprocess_check_call,
)
from .exceptions import ClickableException
from .logger import logger
from .config.project import ProjectConfig


class Device():
    def __init__(self, project: ProjectConfig):
        self.config = project.global_config.device
        self.container_mode = project.container_mode
        self.collect_configs(project)

    def collect_configs(self, project):
        # Long-term plan: Get device settings out of project config

        if project.ssh:
            self.config.ipv4 = project.ssh

        if project.device_serial_number:
            self.config.serial_number = project.device_serial_number

    def detect_adb_attached(self):
        output = run_subprocess_check_output('adb devices -l').strip()
        devices = []
        for line in output.split('\n'):
            if 'device' in line and 'devices' not in line:
                device = line.split(' ')[0]
                for part in line.split(' '):
                    if part.startswith('model:'):
                        device = '{} - {}'.format(
                            device,
                            part.replace('model:', '').replace('_', ' ').strip()
                        )

                devices.append(device)

        return devices

    def check_any_adb_attached(self):
        devices = self.detect_adb_attached()
        if len(devices) == 0:
            raise ClickableException(
                'Cannot access device.\nADB: No devices attached\nSSH: no IP address '
                'specified (--ssh)'
            )

    def check_multiple_adb_attached(self):
        devices = self.detect_adb_attached()
        if len(devices) > 1 and not self.config.serial_number:
            raise ClickableException('Multiple devices detected via adb')

    def get_adb_args(self):
        self.check_any_adb_attached()
        if self.config.serial_number:
            return '-s {}'.format(self.config.serial_number)

        self.check_multiple_adb_attached()
        return ''

    def forward_port_adb(self, port, adb_args):
        command = 'adb {0} forward tcp:{1} tcp:{1}'.format(adb_args, port)
        run_subprocess_check_call(command)

    def push_file(self, src, dst):
        if self.config.ipv4:
            dir_path = os.path.dirname(dst)
            self.run_command('mkdir -p {}'.format(dir_path))
            command = 'scp {} phablet@{}:{}'.format(src, self.config.ipv4, dst)
        else:
            adb_args = self.get_adb_args()
            command = 'adb {} push {} {}'.format(adb_args, src, dst)

        run_subprocess_check_call(command, shell=True)

    def get_ssh_command(self, command, forward_port=None):
        ssh_args = ""

        if forward_port:
            ssh_args = "{0} -L {1}:localhost:{1}".format(ssh_args, forward_port)

        if isinstance(command, list):
            command = " && ".join(command)

        return 'echo "{}" | ssh {} phablet@{}'.format(
            command, ssh_args, self.config.ipv4)

    def get_adb_command(self, command, forward_port=None):
        adb_args = self.get_adb_args()

        if forward_port:
            self.forward_port_adb(forward_port, adb_args)

        if isinstance(command, list):
            command = ";".join(command)

        return 'adb {} shell "{}"'.format(adb_args, command)

    def run_command(self, command, cwd=None, get_output=False, forward_port=None):
        if self.container_mode:
            logger.debug('Skipping device command, running in container mode')
            return None

        if not cwd:
            cwd = os.getcwd()

        wrapped_command = ''
        if self.config.ipv4:
            logger.debug("Accessing {} via SSH".format(self.config.ipv4))
            wrapped_command = self.get_ssh_command(command, forward_port)
        else:
            logger.debug("Accessing device via ADB")
            wrapped_command = self.get_adb_command(command, forward_port)

        if get_output:
            return run_subprocess_check_output(wrapped_command, cwd=cwd, shell=True)

        run_subprocess_check_call(wrapped_command, cwd=cwd, shell=True)
        return None
