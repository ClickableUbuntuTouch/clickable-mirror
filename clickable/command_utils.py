from os.path import dirname, join, basename, isfile
import inspect
import glob

from clickable.commands.base import Command


def get_commands():
    commands = {}
    scr_dir = dirname(__file__)
    modules = glob.glob(join(scr_dir, 'commands/*.py'))
    command_modules = [
        basename(f)[:-3] for f in modules if isfile(f) and not f.endswith('__init__.py')
    ]

    for name in command_modules:
        command_submodule = __import__(
            f'clickable.commands.{name}',
            globals(),
            locals(),
            [name]
        )

        for _, cls in inspect.getmembers(command_submodule):
            if (inspect.isclass(cls)
                    and issubclass(cls, Command)
                    and cls != Command
                    and cls.__name__ not in commands):
                commands[cls.__name__] = cls()

    return commands.values()
