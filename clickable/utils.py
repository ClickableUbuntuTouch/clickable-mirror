import itertools
import subprocess
import re
import os
import shlex
import glob
import inspect
from os.path import dirname, basename, isfile, isdir, join

import yaml

from clickable.builders.base import Builder
from clickable.logger import logger
from clickable.exceptions import FileNotFoundException, ClickableException
from clickable.config.constants import Constants
from clickable.logger import Colors

SCHEMA_VALIDATOR_AVAILABLE = True
try:
    from jsonschema import validate, ValidationError
except ImportError:
    SCHEMA_VALIDATOR_AVAILABLE = False


# TODO use these subprocess functions everywhere


def prepare_command(cmd, shell=False):
    if isinstance(cmd, str):
        if shell:
            cmd = cmd.encode()
        else:
            cmd = shlex.split(cmd)

    if isinstance(cmd, (list, tuple)):
        for idx, x in enumerate(cmd):
            if isinstance(x, str):
                cmd[idx] = x.encode()

    return cmd


def get_existing_dir(name, paths, optional=False):
    for path in paths:
        if isdir(path):
            return path

    if optional:
        logger.debug('%s directory not found.', name)
        return None

    raise ClickableException(f'Cannot find required {name} directory.')


def get_container_mapping():
    if Constants.host_arch in Constants.container_mapping:
        return Constants.container_mapping[Constants.host_arch]

    return {}


def get_container_list():
    return list(get_container_mapping().values())


def run_subprocess_call(cmd, shell=False, **args):
    return subprocess.call(prepare_command(cmd, shell), shell=shell, **args)


def run_subprocess_check_call(cmd, shell=False, cwd=None, **args):
    return subprocess.check_call(prepare_command(cmd, shell), shell=shell, cwd=cwd, **args)


def run_subprocess_check_output(cmd, shell=False, **args):
    return subprocess.check_output(prepare_command(cmd, shell), shell=shell, **args).decode()


def find_pattern(pattern, base_dir, exclude_dir=None):
    # Starting from Python 3.10 we could pass "root_dir=base_dir" instead of changing cwd
    old_cwd = os.getcwd()
    os.chdir(base_dir)
    files = glob.glob(pattern, recursive=True)
    os.chdir(old_cwd)

    files = [os.path.join(base_dir, f) for f in files]

    if exclude_dir:
        files = [f for f in files if not is_sub_dir(f, exclude_dir)]

    return files


def find(
    names,
    cwd,
    temp_dir=None,
    build_dir=None,
    ignore_dir=None,
    extensions_only=False,
    depth=None
):
    found = []
    searchpaths = []
    searchpaths.append(cwd)

    include_build_dir = False
    if build_dir and not build_dir.startswith(os.path.realpath(cwd) + os.sep):
        include_build_dir = True
        searchpaths.append(build_dir)

    for (root, dirs, files) in itertools.chain.from_iterable(
        os.walk(path, topdown=True) for path in searchpaths
    ):
        # Ignore hidden directories
        new_dirs = []
        for d in dirs:
            if os.path.join(root, d) == build_dir or not d[0] == '.':
                new_dirs.append(d)

        dirs[:] = new_dirs

        if depth:
            if include_build_dir and root.startswith(build_dir):
                if root.count(os.sep) >= (build_dir.count(os.sep) + depth):
                    del dirs[:]
            elif root.startswith(cwd):
                if root.count(os.sep) >= (cwd.count(os.sep) + depth):
                    del dirs[:]

        for name in files:
            ok = name in names

            if extensions_only:
                ok = any([name.endswith(n) for n in names])

            if ok:
                if ignore_dir is not None and root.startswith(ignore_dir):
                    continue

                found.append(os.path.join(root, name))

    if not found:
        joined_names = ', '.join(names)
        raise FileNotFoundException(f'Could not find {joined_names}')

    # Favor the manifest in the install dir first, then fall back to the build dir and
    # finally the source dir
    file = ''
    for f in found:
        if temp_dir and f.startswith(os.path.realpath(temp_dir) + os.sep):
            file = f

    if not file:
        for f in found:
            if build_dir and f.startswith(os.path.realpath(build_dir) + os.sep):
                file = f

    if not file:
        file = found[0]

    return file


def is_command(command):
    error_code = run_subprocess_call(
        shlex.split(f'which {command}'),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    return error_code == 0


def check_command(command):
    if not is_command(command):
        raise ClickableException(
            f'The command "{command}" does not exist on this system, please install it for '
            'clickable to work properly'
        )


def get_docker_command():
    command_env = env('CLICKABLE_DOCKER_COMMAND')

    if command_env:
        check_command(command_env)
        return command_env

    for command in ['podman', 'docker']:
        if is_command(command):
            return command

    raise ClickableException(
        'Neither the command "docker" nor "podman" does exist on this system, '
        'please install either on for clickable to work properly'
    )


def env(name):
    value = None
    if name in os.environ and os.environ[name]:
        value = os.environ[name]

    return value


def get_builder(config, container, debug_build=False):
    builder_classes = get_builders()
    return builder_classes[config.builder](config, container, debug_build)


def get_builders():
    builder_classes = {}
    builder_dir = join(dirname(__file__), 'builders')
    modules = glob.glob(join(builder_dir, '*.py'))
    builder_modules = [
        basename(f)[:-3] for f in modules if isfile(f) and not f.endswith('__init__.py')
    ]

    for name in builder_modules:
        builder_submodule = __import__(
            f'clickable.builders.{name}', globals(), locals(), [name]
        )
        for _, cls in inspect.getmembers(builder_submodule):
            if inspect.isclass(cls) and issubclass(cls, Builder) and cls.name:
                builder_classes[cls.name] = cls

    return builder_classes


def get_make_jobs_from_args(make_args):
    for arg in make_args:
        if arg.startswith('-j'):
            jobs_str = arg[2:].strip()
            try:
                return int(jobs_str)
            except ValueError as err:
                raise ClickableException(
                    '"{}" in "make_args" is not a number, but it should be.'
                ) from err

    return None


def merge_make_jobs_into_args(make_args, make_jobs):
    make_args = make_args if make_args else []
    return make_args + [f'-j{make_jobs}']


def flexible_string_to_list(variable, split=False):
    if isinstance(variable, (str, bytes)):
        if split:
            return variable.split()

        return [variable]
    return variable


def load_config_schema(name):
    file_name = f'{name}.schema'
    schema_path = os.path.join(os.path.dirname(__file__), 'config', file_name)
    with open(schema_path, 'r', encoding='UTF-8') as f:
        try:
            return yaml.safe_load(f)
        except ValueError as err:
            raise ClickableException(
                f'Failed reading "{file_name}", it is not valid yaml file'
            ) from err
        return None


def validate_config_format(config, schema, name, path):
    if SCHEMA_VALIDATOR_AVAILABLE:
        try:
            validate(instance=config, schema=schema)
        except ValidationError as e:
            logger.error('The %s config file "%s" contains invalid fields!', name, path)
            error_message = e.message
            # Lets add the key to the invalid value
            if e.path:
                if len(e.path) > 1 and isinstance(e.path[-1], int):
                    error_message = f'{error_message} (in "{e.path[-2]}")'
                else:
                    error_message = f'{error_message} (in "{e.path[-1]}")'
            raise ClickableException(error_message) from e
    else:
        logger.warning('Dependency "jsonschema" not found. Could not validate config file.')


def pull_image(image, skip_existing=True):
    if not skip_existing or not image_exists(image):
        docker_executable = get_docker_command()
        command = f'{docker_executable} pull {image}'
        run_subprocess_check_call(command)


def image_exists(image):
    docker_executable = get_docker_command()
    command = f'{docker_executable} image inspect {image}'
    return run_subprocess_call(
        command,
        stderr=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL
    ) == 0


def image_based_on(image, base):
    docker_executable = get_docker_command()
    command_template = f'{docker_executable} history --no-trunc -q'
    command_base = f'{command_template} {base}'
    command_image = f'{command_template} {image}'

    hash_base = run_subprocess_check_output(command_base).split('\n', 1)[0]
    history = run_subprocess_check_output(command_image).strip()

    return hash_base in history


def makedirs(path):
    os.makedirs(path, 0o777, True)
    return path


def make_absolute(path, change_keys=False):
    if not path:
        return path

    if isinstance(path, list):
        return [make_absolute(p,
                              change_keys=change_keys) for p in path]

    if isinstance(path, dict):
        if change_keys:
            return {make_absolute(key,
                                  change_keys=change_keys): path[key] for key in path}

        return {key: make_absolute(
            path[key], change_keys=change_keys) for key in path}

    if path.startswith('$'):
        return path

    return os.path.abspath(path)


def make_env_var_conform(name):
    return re.sub(r"[^A-Z0-9_]", "_", name.upper())


def is_path_sane(path):
    if isinstance(path, list):
        for p in path:
            if not is_path_sane(p):
                return False
        return True

    return re.match(r"^[$\w\d_\.\-\*\?/@]+$", path)


def is_sub_dir(path, parent):
    path1 = os.path.abspath(path)
    path2 = os.path.abspath(parent)
    return os.path.commonpath([path1, path2]).startswith(path2)


def let_user_confirm(message, default=True):
    options = 'Y/n' if default else 'y/N'
    question = f'{message} [{options}]: '

    choice = input(Colors.INFO + question + Colors.CLEAR).strip().lower()

    if choice == '':
        return default

    return choice in ['y', 'yes']
