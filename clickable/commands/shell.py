import subprocess
import os
import shlex

from clickable.utils import (
    run_subprocess_call,
    run_subprocess_check_output,
)
from clickable.logger import logger
from clickable.exceptions import ClickableException

from .base import Command


class ShellCommand(Command):
    def __init__(self):
        Command.__init__(self)
        self.cli_conf.name = 'shell'
        self.cli_conf.help_msg = 'Opens a shell on the device via ssh'
        self.aliases = ['ssh']

    def toggle_ssh(self, on=False):
        toggle = 'true' if on else 'false'
        command = 'sudo -u phablet bash -c \'/usr/bin/gdbus call -y -d ' \
                  'com.canonical.PropertyService -o /com/canonical/PropertyService ' \
                  f'-m com.canonical.PropertyService.SetProperty ssh {toggle}\''

        adb_args = ''
        if self.config.device_serial_number:
            adb_args = f'-s {self.config.device_serial_number}'

        run_subprocess_call(
            shlex.split(f'adb {adb_args} shell "{command}"'),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

    def setup_ssh_via_adb(self):
        self.device.check_any_adb_attached()

        adb_args = ''
        if self.config.device_serial_number:
            adb_args = f'-s {self.config.device_serial_number}'
        else:
            self.device.check_multiple_adb_attached()

        output = run_subprocess_check_output(
            shlex.split(f'adb {adb_args} shell pgrep sshd')
        ).split()
        if not output:
            self.toggle_ssh(on=True)

        # Use the usb cable rather than worrying about going over wifi
        port = 0
        for p in range(2222, 2299):
            error_code = run_subprocess_call(
                shlex.split(f'adb {adb_args} forward tcp:{p} tcp:22'),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            if error_code == 0:
                port = p
                break

        if port == 0:
            raise ClickableException('Failed to open a port to the device')

        # Purge the device host key so that SSH doesn't print a scary warning about it
        # (it changes every time the device is reflashed and this is expected)
        known_hosts = os.path.expanduser('~/.ssh/known_hosts')
        subprocess.check_call(shlex.split(f'touch {known_hosts}'))
        subprocess.check_call(
            shlex.split(f'ssh-keygen -f {known_hosts} -R [localhost]:{port}')
        )

        ssh_dir = os.path.expanduser('~/.ssh/')
        id_pub_candidates = ["id_rsa.pub", "id_ed25519.pub"]
        id_pub = None

        for cand in id_pub_candidates:
            path = os.path.join(ssh_dir, cand)
            if os.path.isfile(path):
                id_pub = path

        if not id_pub:
            logger.warning(
                'Could not find any ssh public key (%s) in %s, '
                'please generate one and try again if the connection is refused.',
                ' or '.join(id_pub_candidates), ssh_dir,
            )
            return port

        with open(id_pub, 'r', encoding='UTF-8') as f:
            public_key = f.read().strip()

        self.device.run_command('[ -d ~/.ssh ] || mkdir ~/.ssh')
        self.device.run_command('touch  ~/.ssh/authorized_keys')

        output = run_subprocess_check_output(
            f'adb {adb_args} shell "grep \\"{public_key}\\" ~/.ssh/authorized_keys"',
            shell=True
        ).strip()
        if not output or 'No such file or directory' in output:
            logger.info('Inserting ssh public key on the connected device')
            self.device.run_command(f'echo \"{public_key}\" >>~/.ssh/authorized_keys')
            self.device.run_command('chmod 700 ~/.ssh')
            self.device.run_command('chmod 600 ~/.ssh/authorized_keys')

        return port

    def run(self):
        '''
        Inspired by
        http://bazaar.launchpad.net/~phablet-team/phablet-tools/trunk/view/head:/phablet-shell
        '''
        if self.config.ssh:
            subprocess.check_call(shlex.split(f'ssh phablet@{self.config.ssh}'))
        else:
            port = self.setup_ssh_via_adb()

            subprocess.check_call(
                shlex.split(
                    'ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no '
                    f'-p {port} phablet@localhost'
                )
            )
            self.toggle_ssh(on=False)
