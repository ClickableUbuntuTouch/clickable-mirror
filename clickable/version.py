from os.path import expanduser, isfile
from datetime import datetime, timedelta
import json

from clickable.logger import logger, log_file, console_handler

requests_available = True
try:
    import requests
except ImportError:
    requests_available = False

__version__ = '6.24.1'
__container_minimum_required__ = 2

DATE_FORMAT = '%Y-%m-%dT%H:%M:%S'

def show_version():
    logger.info('clickable ' + __version__)
    check_version()

def check_version(quiet=False):
    if requests_available:
        version = None
        check = True
        version_check = expanduser('~/.clickable/version_check.json')
        if isfile(version_check):
            with open(version_check, 'r') as f:
                try:
                    version_check_data = json.load(f)
                except ValueError:
                    version_check_data = None

            if version_check_data and 'version' in version_check_data and 'datetime' in version_check_data:
                last_check = datetime.strptime(version_check_data['datetime'], DATE_FORMAT)
                if last_check > (datetime.now() - timedelta(days=2)) and \
                    'current_version' in version_check_data and \
                    version_check_data['current_version'] == __version__:

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
            except requests.exceptions.Timeout as e:
                logger.warning('Unable to check for updates to clickable, the request timedout')
            except Exception as e:
                logger.debug('Version check failed:' + str(e.cmd), exc_info=e)
                logger.warning('Unable to check for updates to clickable, an unknown error occurred')

            if version:
                with open(version_check, 'w') as f:
                    json.dump({
                        'version': version,
                        'datetime': datetime.now().strftime(DATE_FORMAT),
                        'current_version': __version__,
                    }, f)

        if version:
            if version != __version__:
                logger.info('v{} of clickable is available, update to get the latest features and improvements!'.format(version))
            else:
                if not quiet:
                    logger.info('You are running the latest version of clickable!')
    else:
        if not quiet:
            logger.warning('Unable to check for updates to clickable, please install "requests"')

