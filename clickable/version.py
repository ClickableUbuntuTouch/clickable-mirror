from datetime import datetime, timedelta
import os
import json
import re

from clickable.config.constants import Constants
from clickable.logger import logger

REQUESTS_AVAILABLE = True
try:
    import requests
except ImportError:
    REQUESTS_AVAILABLE = False

__version__ = '8.3.0'

__container_minimum_required__ = 11

DATE_FORMAT = '%Y-%m-%dT%H:%M:%S'


def show_version():
    logger.info('clickable ' + __version__)
    check_version()


def split_version_numbers(version_string):
    return [
        int(n) for n in re.split(r'\.', version_string)
    ]


def get_major_version():
    return split_version_numbers(__version__)[0]


def is_newer_than_running(version_numbers):
    running_version = split_version_numbers(__version__)

    # Compare all numbers until finding an unequal pair
    for check, running in zip(version_numbers, running_version):
        if check < running:
            return False
        if check > running:
            return True

    return len(version_numbers) > len(running_version)


def check_version(quiet=False, force_download=False):
    if REQUESTS_AVAILABLE:
        version = None
        check = True
        version_check = os.path.join(Constants.clickable_dir, 'version_check.json')
        if os.path.isfile(version_check) and not force_download:
            with open(version_check, 'r', encoding='UTF-8') as f:
                try:
                    version_check_data = json.load(f)
                except ValueError:
                    version_check_data = None

            if (
                version_check_data and
                'version' in version_check_data and
                'datetime' in version_check_data
            ):
                last_check = datetime.strptime(version_check_data['datetime'], DATE_FORMAT)
                if (
                    last_check > (datetime.now() - timedelta(days=2)) and
                    'current_version' in version_check_data and
                    version_check_data['current_version'] == __version__
                ):
                    check = False
                    version = version_check_data['version']
                    logger.debug('Using cached version check')

        if check:
            logger.debug('Checking for updates to clickable')

            try:
                response = requests.get(
                    'https://clickable-ut.dev/en/latest/_static/version.json',
                    timeout=5
                )
                response.raise_for_status()

                data = response.json()
                version = data['version']
            except requests.exceptions.Timeout:
                logger.warning('Unable to check for updates to clickable, the request timedout')
            except requests.exceptions.ConnectionError:
                logger.warning(
                    'Unable to check for updates to clickable. Are you connected to the internet?')
            except requests.exceptions.RequestException as e:
                logger.debug('Version check failed:' + str(e), exc_info=e)
                logger.warning(
                    'Unable to check for updates to clickable, an unknown error occurred')

            if version:
                with open(version_check, 'w', encoding='UTF-8') as f:
                    json.dump({
                        'version': version,
                        'datetime': datetime.now().strftime(DATE_FORMAT),
                        'current_version': __version__,
                    }, f)

        if version:
            version_numbers = split_version_numbers(version)
            if is_newer_than_running(version_numbers):
                logger.info(
                    'v%s of clickable is available, update to get the latest features '
                    'and improvements!', version
                )
            else:
                if not quiet:
                    logger.info('You are running the latest version of clickable!')
    else:
        if not quiet:
            logger.warning('Unable to check for updates to clickable, please install "requests"')
