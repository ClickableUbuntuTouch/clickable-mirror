#!/usr/bin/env python3
# PYTHON_ARGCOMPLETE_OK

try:
    import argcomplete
    HAS_ARGCOMPLETE = True
except ImportError:
    HAS_ARGCOMPLETE = False

import sys
import subprocess
import logging
import platform

from clickable.config.constants import Constants
from clickable.logger import logger, log_file, console_handler
from clickable.exceptions import ClickableException
from clickable.cli import Cli
from clickable.version import __version__, check_version
from clickable.command_utils import get_commands


class Clickable():
    def __init__(self):
        self.cli = Cli()
        self.verbose = True
        self.commands = get_commands()

    def create_parser(self):
        for cmd in self.commands:
            self.cli.add_cmd_parser(cmd)

    def run(self):
        if HAS_ARGCOMPLETE:
            argcomplete.autocomplete(self.cli.parser)
        else:
            logger.debug('argcomplete is not installed')

        args = self.cli.parse_args(sys.argv[1:])

        self.verbose = 'verbose' in args and args.verbose
        if self.verbose:
            console_handler.setLevel(logging.DEBUG)
        logger.debug('Clickable v' + __version__)

        if not Constants.host_arch:
            raise ClickableException(
                f"No support for host architecture {platform.machine()}"
            )

        if "func" not in args:
            default = ['default']
            if self.verbose:
                default += ['--verbose']

            args = self.cli.parse_args(default)

        args.func(args)


def main():
    clickable = Clickable()

    try:
        clickable.create_parser()

        is_version_check = '--version' in sys.argv[1:] or '-v' in sys.argv[1:]
        check_version(quiet=True, force_download=is_version_check)

        clickable.run()
    except ClickableException as e:
        logger.error(str(e))
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        logger.debug('Command exited with an error:' + str(e.cmd), exc_info=e)
        logger.critical(
            'Command exited with non-zero exit status %s, see above for details. '
            'This is most likely not a problem with Clickable.', e.returncode
        )

        sys.exit(2)
    except KeyboardInterrupt:
        logger.info('')  # Print an empty space at then end so the cli prompt is nicer
        sys.exit(0)
    except Exception as e:  # pylint: disable=broad-except
        if isinstance(e, OSError) and '28' in str(e):
            logger.critical('No space left on device')
            sys.exit(2)

        logger.debug('Encountered an unknown error', exc_info=e)
        if not clickable.verbose:
            logger.critical('Encountered an unknown error: ' + str(e))

        logger.critical(
            'If you believe this is a bug, please file a report at '
            'https://gitlab.com/clickable/clickable/issues with the log file located at ' +
            log_file
        )
        sys.exit(3)


if __name__ == '__main__':
    main()
