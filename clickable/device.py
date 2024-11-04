import os
import shutil
import getpass
from subprocess import CalledProcessError, TimeoutExpired

from .utils import (
    run_subprocess_check_output,
    run_subprocess_check_call,
)
from .exceptions import ClickableException
from .logger import logger
from .config.device import DeviceConfig
from .config.constants import Constants


class Device():
    def __init__(self, config: DeviceConfig):
        self.config = config
        self.connection = None
        self.device_arch = None
        self.ssh_welcome_touched = False

        self.determine_device()

    def determine_device(self):
        detect_command = "dpkg --print-architecture"

        if self.config.selection == 'detect':
            self.detect_connection(detect_command)
        else:
            self.connection = self.config.selection
            self.detect_arch(detect_command)

    def detect_connection(self, detect_command):
        if self.config.default_target == 'host':
            self.set_host_device()
            return

        adb_checked = False
        if self.config.default_target == 'adb':
            adb_checked = True
            if self.detect_adb_arch(detect_command):
                return

        if self.detect_ssh_arch(detect_command):
            return

        if not adb_checked:
            if self.detect_adb_arch(detect_command):
                return

        self.set_no_device()

    def detect_arch(self, detect_command):
        if self.connection == 'adb':
            if not self.detect_adb_arch(detect_command):
                self.set_no_device()
        elif self.connection == 'ssh':
            if not self.detect_ssh_arch(detect_command):
                self.set_no_device()
        elif self.connection == 'host':
            self.set_host_device()
        else:
            raise ClickableException(f'Connection type {self.connection} not supported.')

    def detect_ssh_arch(self, detect_command):
        if not self.config.ipv4:
            return None

        logger.info('Trying to detect device via SSH at %s ...', self.config.ipv4)
        command = self.get_ssh_command(detect_command)

        try:
            self.touch_ssh_welcome_message()
            self.device_arch = run_subprocess_check_output(command, shell=True).strip()
            self.connection = 'ssh'
            logger.info("Detected %s device via SSH", self.device_arch)
            return True
        except CalledProcessError:
            logger.debug('SSH architecture detection failed')
            return False

    def detect_adb_arch(self, detect_command):
        if not self.is_any_adb_attached():
            logger.debug('No ADB device attached')
            return False

        if not self.is_adb_device_defined():
            logger.warning(
                'Multiple ADB device attached, but no matching serial number configured')
            return False

        command = self.get_adb_command(detect_command)
        try:
            self.device_arch = run_subprocess_check_output(command, shell=True, timeout=5).strip()
        except TimeoutExpired:
            if self.config.xenial_adb:
                raise

            self.config.xenial_adb = True
            logger.warning(
                "ADB architecture detection timed out. Retrying, assuming a xenial device...")
            return self.detect_adb_arch(detect_command)

        self.connection = 'adb'
        logger.info("Detected %s device via ADB", self.device_arch)

        return True

    def set_host_device(self):
        self.connection = 'host'
        self.device_arch = Constants.host_arch

        logger.info("Running in Host Mode.")

        if getpass.getuser() != 'phablet':
            logger.warning('The host device does not seem to be a Ubuntu Touch device.')

    def set_no_device(self):
        if self.config.required:
            raise ClickableException('No device detected')

        logger.info("No device detected")

        self.connection = None
        self.device_arch = None

    def is_any_adb_attached(self):
        return len(detect_adb_attached()) >= 1

    def is_adb_device_defined(self):
        devices = detect_adb_attached()

        return (len(devices) == 1 or
                self.config.serial_number and self.config.serial_number in devices)

    def get_adb_args(self):
        if self.config.serial_number:
            return f'-s {self.config.serial_number}'

        return ''

    def forward_port_adb_with_args(self, host, target, adb_args):
        command = f'adb {adb_args} forward tcp:{host} tcp:{target}'
        run_subprocess_check_call(command)

    def forward_port_adb(self, host, target):
        self.forward_port_adb_with_args(host, target, self.get_adb_args())

    def touch_ssh_welcome_message(self):
        if not self.ssh_welcome_touched:
            omit_welcome_command = self.get_ssh_command("touch /home/phablet/.hushlogin")
            run_subprocess_check_call(omit_welcome_command, shell=True)
            self.ssh_welcome_touched = True

    def push_file(self, src, dst):
        dir_path = os.path.dirname(dst)
        self.run_command(f'mkdir -p {dir_path}')

        if self.connection == "ssh":
            command = ['scp']

            if self.config.ssh_port:
                command += ['-o', f'Port={self.config.ssh_port}']

            command += [src, f'phablet@{self.config.ipv4}:{dst}']
            command = " ".join(command)
        elif self.connection == "adb":
            adb_args = self.get_adb_args()
            command = f'adb {adb_args} push {src} {dst}'
        elif self.connection == "host":
            shutil.copy(src, dst)
            return
        else:
            raise ClickableException(
                f'File pushing not implemented for connection type {self.connection}')

        run_subprocess_check_call(command, shell=True)

    def get_adb_command(self, command, forward_port=None):
        adb_args = self.get_adb_args()

        if forward_port:
            self.forward_port_adb_with_args(forward_port, forward_port, adb_args)

        if isinstance(command, list):
            command = ";".join(command)

        if self.config.xenial_adb:
            return f'adb {adb_args} shell "{command}"'

        return f'echo "{command} || echo ADB_COMMAND_FAILED" | adb {adb_args} shell'

    def get_ssh_command(self, command, *args, **kwargs):
        return assemble_ssh_command(
            self.config.ipv4, self.config.ssh_port, command, *args, **kwargs)

    def run_command(self, command, cwd=None, get_output=False, forward_port=None):
        if not cwd:
            cwd = os.getcwd()

        wrapped_command = ''
        if self.connection == "ssh":
            logger.debug("Accessing %s via SSH", self.config.ipv4)
            self.touch_ssh_welcome_message()
            wrapped_command = self.get_ssh_command(command, forward_port)
        elif self.connection == "adb":
            logger.debug("Accessing device via ADB")
            wrapped_command = self.get_adb_command(command, forward_port)
        elif self.connection == "host":
            logger.debug("Running command on host device")
            wrapped_command = command
        else:
            raise ClickableException(
                'Running commands on device not implemented for connection type '
                f'{self.config.connection}')

        output = run_subprocess_check_output(wrapped_command, cwd=cwd, shell=True)

        if self.connection == "adb" and output.strip().endswith("ADB_COMMAND_FAILED"):
            print(output)
            raise ClickableException("Command ran on device via ADB failed. See output above.")

        if not get_output:
            print(output)

        return output


def detect_adb_attached():
    output = run_subprocess_check_output('adb devices -l').strip()
    devices = []
    for line in output.split('\n'):
        if 'device' in line and 'devices' not in line:
            device = line.split(' ')[0]
            for part in line.split(' '):
                if part.startswith('model:'):
                    model = part.replace('model:', '').replace('_', ' ').strip()
                    device = f'{device} - {model}'

            devices.append(device)

    return devices


def assemble_ssh_command(ipv4, ssh_port, command, forward_port=None, interactive=False):
    ssh_args = "" if interactive else "-T"

    if ssh_port:
        ssh_args = f"{ssh_args} -o Port={ssh_port}"

    if forward_port:
        ssh_args = f"{ssh_args} -L {forward_port}:localhost:{forward_port}"

    if isinstance(command, list):
        command = " && ".join(command)

    command_pipe = f'echo "{command}" | ' if command else ""

    return f'{command_pipe} ssh {ssh_args} phablet@{ipv4}'
