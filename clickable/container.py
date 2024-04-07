import subprocess
import shlex
import os
import shutil
import getpass
import uuid
import sys
import json

from clickable.utils import (
    image_based_on,
    run_subprocess_check_call,
    run_subprocess_check_output,
    get_docker_command,
    image_exists,
    env,
    check_command,
)
from clickable.logger import logger
from clickable.config.constants import Constants
from clickable.exceptions import ClickableException
from clickable.version import __container_minimum_required__


class Container():
    def __init__(self, config, name=None, minimum_version=None):
        self.config = config
        self.docker_mode = self.config.needs_docker()
        self.minimum_version = minimum_version \
            if minimum_version \
            else __container_minimum_required__
        self.docker_image = self.config.docker_image
        self.base_docker_image = self.docker_image

        self.docker_desktop = False

        if self.docker_mode:
            self.docker_executable = get_docker_command()
            if self.docker_executable == 'docker':
                format_args = "{{.OperatingSystem}}"
                command = f'{self.docker_executable} info --format {format_args}'
                self.docker_desktop = 'Docker Desktop' in run_subprocess_check_output(command)

            self.clickable_dir = f'.clickable/{self.config.build_arch}'
            if name:
                self.clickable_dir = f'{self.clickable_dir}/{name}'

            self.docker_name_file = f'{self.clickable_dir}/image.json'
            self.docker_file = f'{self.clickable_dir}/Dockerfile'

            if self.needs_customized_container():
                self.restore_cached_image()

        if self.config.builder == Constants.RUST and self.config.cargo_home:
            logger.debug("Caching cargo related files in %s",
                         self.config.cargo_home)

    def restore_cached_image(self):
        if not os.path.exists(self.docker_name_file):
            return

        with open(self.docker_name_file, 'r', encoding='UTF-8') as f:
            cached_image = None
            cached_base_image = None

            try:
                image_file = json.load(f)
                cached_image = image_file.get('name', None)
                cached_base_image = image_file.get('base_image', None)
            except ValueError:
                pass

            if not cached_image:
                logger.warning("Cached image file is invalid")
                return

            if not image_exists(cached_image):
                logger.warning("Cached container does not exist anymore")
                return

            if self.base_docker_image != cached_base_image:
                logger.warning("Cached image has a different base image")

            self.check_docker()

            if image_based_on(cached_image, self.base_docker_image):
                logger.debug("Found cached container")
                self.docker_image = cached_image
            else:
                logger.warning("Cached container is outdated")

    def start_docker(self):
        check_command('systemctl')
        if self.docker_executable == 'docker':
            logger.info('Asking for root to start docker')
            run_subprocess_check_output(shlex.split('sudo systemctl start docker'))

    def is_docker_service_running(self):
        if env('CLICKABLE_SKIP_DOCKER_CHECKS'):
            return True

        check_command('systemctl')

        try:
            run_subprocess_check_output(
                'systemctl is-active --quiet snap.docker.dockerd.service',
                stderr=subprocess.STDOUT)
            return True
        except subprocess.CalledProcessError:
            pass

        try:
            run_subprocess_check_output(
                'systemctl is-active --quiet docker',
                stderr=subprocess.STDOUT)
            return True
        except subprocess.CalledProcessError:
            pass

        try:
            run_subprocess_check_output(
                'systemctl --user is-active --quiet docker-desktop',
                stderr=subprocess.STDOUT)
            return True
        except subprocess.CalledProcessError:
            pass

        return False

    def check_docker(self):
        if not self.docker_mode:
            raise ClickableException(
                "Container was not initialized with Container Mode. "
                "This seems to be a bug in Clickable."
            )

        if self.docker_executable != 'docker':
            logger.debug('Skipping docker check as %s is used instead.', self.docker_executable)
            return

        if env('CLICKABLE_SKIP_DOCKER_CHECKS'):
            logger.debug('Skipping docker check because of env var.')
            return

        if not self.is_systemd_used():
            logger.debug('Skipping docker check because systemd is not used.')
            return

        if self.is_docker_ready():
            return

        raise ClickableException('Docker is not running or not properly set up.\n'
                                 'Please run "clickable setup docker" first.')

    def is_systemd_used(self):
        if sys.platform != "linux":
            return False

        with open('/proc/1/comm', 'r', encoding='UTF-8') as f:
            init_system = f.read().strip()
            return init_system == "systemd"

    def docker_group_exists(self):
        if sys.platform != "linux":
            return False

        group_exists = False
        with open('/etc/group', 'r', encoding='UTF-8') as f:
            lines = f.readlines()
            for line in lines:
                if line.startswith('docker:'):
                    group_exists = True

        return group_exists

    def user_in_docker_group_pending(self):
        return self.user_in_docker_group() and not self.proccess_in_docker_group()

    def proccess_in_docker_group(self):
        check_command('groups')

        groups = run_subprocess_check_output(shlex.split('groups')).strip().split()

        return 'docker' in groups

    def user_in_docker_group(self):
        check_command('groups')

        groups = run_subprocess_check_output(
            shlex.split(f'groups {getpass.getuser()}')
        ).strip().split()

        return 'docker' in groups

    def is_docker(self):
        return self.docker_executable == 'docker' and self.docker_mode

    def is_docker_ready(self):
        return self.is_docker_configured() and self.is_docker_service_running()

    def setup_docker(self):
        if self.docker_executable != 'docker':
            logger.debug('Skipping docker setup as %s is used instead.', self.docker_executable)
            return

        logger.info('Setting up docker')

        if not self.is_docker_service_running():
            self.start_docker()

        if not self.docker_group_exists():
            logger.info('Asking for root to create docker group')
            subprocess.check_call(shlex.split('sudo groupadd docker'))

        if not self.user_in_docker_group():
            logger.info('Asking for root to add the current user to the docker group')
            subprocess.check_call(
                shlex.split(f'sudo usermod -aG docker {getpass.getuser()}')
            )

        logger.info('Setup finished')

        if self.user_in_docker_group_pending():
            raise ClickableException('Please log out or restart to complete')

    def is_docker_configured(self):
        check_command('docker')

        if self.docker_desktop:
            return True

        return self.docker_group_exists() and self.proccess_in_docker_group()

    def pull_files(self, files, dst_parent):
        os.makedirs(dst_parent, exist_ok=True)

        if self.config.container_mode:
            for f in files:
                dst_path = os.path.join(dst_parent, os.path.basename(f))
                if os.path.isdir(f):
                    if os.path.exists(dst_path):
                        shutil.rmtree(dst_path)
                    shutil.copytree(f, dst_path)
                else:
                    if os.path.exists(dst_path):
                        os.remove(dst_path)
                    shutil.copy(f, dst_parent, follow_symlinks=False)
        else:  # Docker
            mounts = self.render_mounts(
                self.get_docker_mounts(transparent=[self.config.root_dir]))
            command_create = f'{self.docker_executable} create {mounts} {self.docker_image}'
            container = run_subprocess_check_output(command_create).strip()

            for f in files:
                command_copy = f'{self.docker_executable} cp {container}:{f} {dst_parent}'
                run_subprocess_check_call(command_copy)

            command_remove = f'{self.docker_executable} rm {container}'
            run_subprocess_check_call(command_remove,
                                      stdout=subprocess.DEVNULL)

    def get_docker_mounts(self, transparent=None):
        # container path is key, host path is value
        mounts = {}

        if self.config.builder == Constants.GO and self.config.gopath:
            gopaths = self.config.gopath.split(':')
            for (index, path) in enumerate(gopaths):
                mounts[f'/gopath/path{index}'] = path
                os.makedirs(path, exist_ok=True)

        if self.config.builder == Constants.RUST and self.config.cargo_home:
            cargo_registry = os.path.join(self.config.cargo_home, 'registry')
            cargo_git = os.path.join(self.config.cargo_home, 'git')
            cargo_package_cache_lock = os.path.join(self.config.cargo_home,
                                                    '.package-cache')

            os.makedirs(cargo_registry, exist_ok=True)
            os.makedirs(cargo_git, exist_ok=True)

            # create .package-cache if it doesn't exist
            with open(cargo_package_cache_lock, "a", encoding='UTF-8'):
                pass

            mounts['/opt/rust/cargo/registry'] = cargo_registry
            mounts['/opt/rust/cargo/git'] = cargo_git
            mounts['/opt/rust/cargo/.package-cache'] = cargo_package_cache_lock

        if transparent:
            for path in transparent:
                mounts[path] = path

        return mounts

    def render_mounts(self, mounts):
        return " ".join([
            f"-v {host}:{container}:Z"
            for container, host in mounts.items()
        ])

    def render_id_mapping_string(self, mapid=os.getuid()):
        if self.docker_executable == 'podman':
            uidmap = self.render_single_id_mapping_string('--uidmap', mapid)
            gidmap = self.render_single_id_mapping_string('--gidmap', mapid)
            return f'{uidmap} {gidmap}'

        return ''

    def render_single_id_mapping_string(self, flag, mapid):
        # e.g. "--uidmap 1000:0:1 --uidmap 0:1:1000"
        return f'{flag} {mapid}:0:1 {flag} 0:1:{mapid}'

    def run_command(self,
                    command,
                    root_user=False,
                    get_output=False,
                    use_build_dir=True,
                    cwd=None,
                    tty=False,
                    localhost=False):
        wrapped_command = command
        cwd = cwd if cwd else os.path.abspath(self.config.root_dir)

        if self.config.container_mode:
            wrapped_command = f'bash -c "{command}"'
        else:  # Docker
            self.check_docker()

            if self.config.first_docker_info:
                logger.debug('Using docker container "%s"', self.docker_image)
                self.config.first_docker_info = False

            go_config = ''
            if self.config.builder == Constants.GO and self.config.gopath:
                gopaths = self.config.gopath.split(':')
                docker_gopaths = [
                    f'/gopath/path{index}'
                    for index in range(len(gopaths))
                ]
                joined_go_paths = ':'.join(docker_gopaths)
                go_config = f'-e GOPATH={joined_go_paths}'

            env_vars = self.config.prepare_docker_env_vars()

            user = ""
            if self.docker_desktop:
                user = '--user 0:0'
            elif not root_user:
                user = f"--user {os.getuid()}"

            id_mappings = self.render_id_mapping_string()

            mounts = self.render_mounts(
                self.get_docker_mounts(transparent=[cwd, self.config.root_dir]))

            command_cwd = self.config.build_dir if use_build_dir else cwd
            command_tty = "-t" if tty else ""
            network = '--network="host"' if localhost else ""

            # make sure PID 1 process handles signals
            if not tty:
                command = f'''
set -Eeou pipefail
trap "exit" SIGINT
trap "exit" SIGTERM
{command} &
bg_pid=$!
wait $bg_pid
exit $?
                '''.strip()

            wrapped_command = f'''{self.docker_executable} run {mounts} {env_vars} {go_config}
                {user} {id_mappings} -w {command_cwd} --rm {command_tty} {network}
                -i {self.docker_image} bash -c "{command}"'''

        kwargs = {}
        if use_build_dir:
            kwargs['cwd'] = self.config.build_dir

        logger.debug("Complete command to run:\n%s", wrapped_command)

        if get_output:
            return run_subprocess_check_output(shlex.split(wrapped_command), **kwargs)

        subprocess.check_call(shlex.split(wrapped_command), **kwargs)
        return None

    def get_dependency_packages(self):
        dependencies = self.config.dependencies_host
        for dep in self.config.dependencies_target:
            if ':' in dep:
                dependencies.append(dep)
            else:
                dependencies.append(f'{dep}:{self.config.arch}')
        return dependencies

    def get_ppa_adding_commands(self):
        if self.config.dependencies_ppa:
            return [
                f'add-apt-repository -y {ppa}'
                for ppa in self.config.dependencies_ppa
            ]

        return []

    def construct_dockerfile_content(self, commands, env_vars, args):
        env_lines = ''

        args_strings = [
            f'ARG {key}="{var}"' for key, var in args.items()
        ]

        env_strings = [
            f'{key}="{var}"' for key, var in env_vars.items()
        ]

        run_strings = [
            f'RUN {cmd}' for cmd in commands
        ]

        args_lines = '\n'.join(args_strings)
        if env_strings:
            env_lines = 'ENV ' + ' '.join(env_strings)
        run_lines = '\n'.join(run_strings)

        return f'''
FROM {self.base_docker_image}
{args_lines}
{env_lines}
{run_lines}
        '''.strip()

    def create_custom_container(self, dockerfile_content):
        if not os.path.exists(self.clickable_dir):
            os.makedirs(self.clickable_dir)

        with open(self.docker_file, 'w', encoding='UTF-8') as f:
            f.write(dockerfile_content)

        self.docker_image = f'{self.base_docker_image}-{uuid.uuid4()}'
        with open(self.docker_name_file, 'w', encoding='UTF-8') as f:
            json.dump({
                'name': self.docker_image,
                'base_image': self.base_docker_image,
            }, f)

        logger.debug('Generating new docker image')
        try:
            subprocess.check_call(
                shlex.split(f'{self.docker_executable} build -t {self.docker_image} .'),
                cwd=self.clickable_dir
            )
        except subprocess.CalledProcessError:
            self.clean_clickable()
            raise

    def is_dockerfile_outdated(self, dockerfile_content):
        if self.docker_image == self.base_docker_image:
            return True

        if not os.path.exists(self.clickable_dir):
            return True

        if not os.path.exists(self.docker_file):
            return True

        with open(self.docker_file, 'r', encoding='UTF-8') as f:
            if dockerfile_content.strip() != f.read().strip():
                return True

        return not image_exists(self.docker_image)

    def get_apt_install_cmd(self, dependencies):
        joined_deps = ' '.join(dependencies)
        return f'apt-get install -y --force-yes --no-install-recommends {joined_deps}'

    def setup_customized_image(self):
        logger.debug('Checking dependencies and image setup')

        self.check_docker()

        commands = []
        env_vars = self.config.image_setup.get('env', {})
        args = self.config.get_env_vars()

        commands += self.get_ppa_adding_commands()

        dependencies = self.get_dependency_packages()
        if dependencies:
            commands.append(
                'echo set debconf/frontend Noninteractive | debconf-communicate && '
                'echo set debconf/priority critical | debconf-communicate'
            )
            dependencies_cmd = self.get_apt_install_cmd(dependencies)
            commands.append(
                f'apt-get update && {dependencies_cmd} && apt-get clean')

        if self.config.rust_channel:
            commands.append(f'rustup default {self.config.rust_channel}')

            if self.config.is_foreign_target():
                commands.append(f'rustup target add {self.config.arch_rust}')

        if self.config.image_setup:
            commands.extend(self.config.image_setup.get('run', []))

        dockerfile_content = self.construct_dockerfile_content(commands, env_vars, args)

        if self.is_dockerfile_outdated(dockerfile_content):
            self.create_custom_container(dockerfile_content)
        else:
            logger.debug('Image already setup')

    def setup_container_mode(self):
        ppa_commands = self.get_ppa_adding_commands()
        if ppa_commands:
            self.run_command(' && '.join(ppa_commands))

        dependencies = self.get_dependency_packages()
        if dependencies:
            self.run_command('apt-get update', use_build_dir=False)

            run = False
            for dep in dependencies:
                exists = ''
                try:
                    exists = self.run_command(
                        f'dpkg -s {dep} | grep Status',
                        get_output=True,
                        use_build_dir=False
                    )
                except subprocess.CalledProcessError:
                    exists = ''

                if exists.strip() != 'Status: install ok installed':
                    run = True
                    break

            if run:
                self.run_command(
                    self.get_apt_install_cmd(dependencies),
                    use_build_dir=False
                )
            else:
                logger.debug('Dependencies already installed')

        if self.config.rust_channel:
            self.run_command(f'rustup default {self.config.rust_channel}')

            if self.config.is_foreign_target():
                self.run_command(f'rustup target add {self.config.arch_rust}')

        if self.config.image_setup:
            os.environ.update(self.config.image_setup.get('env', {}))
            for command in self.config.image_setup.get('run', []):
                self.run_command(command, use_build_dir=False)

    def needs_customized_container(self):
        return not self.config.skip_image_setup and (
            self.config.dependencies_host
            or self.config.dependencies_target
            or self.config.dependencies_ppa
            or self.config.image_setup
            or self.config.rust_channel)

    def check_base_image_version(self):
        if not self.minimum_version or self.config.is_custom_docker_image:
            return

        if not image_exists(self.docker_image):
            return

        version = 0
        try:
            format_string = '{{ index .Config.Labels "image_version"}}'
            command = f"\
                {self.docker_executable} inspect --format '{format_string}' {self.docker_image} \
            "
            logger.debug('Checking docker image version via: %s', command)

            version_string = run_subprocess_check_output(command)
            version = int(version_string)
        except (ValueError, subprocess.CalledProcessError):
            logger.warning("Could not read the image version from the container")

        if version < self.minimum_version:
            raise ClickableException(
                f'This version of Clickable requires Clickable docker image {self.docker_image} '
                f'in version {self.minimum_version} or higher (found version {version}). '
                'Please run "clickable update-images" to update your local images.'
            )

    def setup(self):
        if self.docker_mode:
            self.check_base_image_version()

        if not self.config.skip_image_setup:
            if self.config.container_mode:
                self.setup_container_mode()
            elif self.needs_customized_container():
                self.setup_customized_image()

        self.config.set_env_vars()

    def clean_clickable(self):
        path = os.path.join(self.config.cwd, self.clickable_dir)
        if os.path.exists(path):
            try:
                shutil.rmtree(path)
            except Exception:  # pylint: disable=broad-except
                typ, value, _ = sys.exc_info()
                # TODO see if there is a proper way to do this
                if typ == OSError and 'No such file or directory' in value:
                    pass  # Nothing to do here, the directory didn't exist
                else:
                    raise
