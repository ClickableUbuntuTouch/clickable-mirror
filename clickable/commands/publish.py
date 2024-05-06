import os
import urllib.parse

from requests.exceptions import ConnectTimeout, ReadTimeout

from clickable.logger import logger
from clickable.exceptions import ClickableException
from clickable.utils import env

from .base import Command

REQUESTS_AVAILABLE = True
try:
    import requests
except ImportError:
    REQUESTS_AVAILABLE = False


OPENSTORE_API = 'https://open-store.io'
OPENSTORE_API_PATH = '/api/v3/manage/{}/revision'


class PublishCommand(Command):
    def __init__(self):
        super().__init__()
        self.cli_conf.name = 'publish'
        self.cli_conf.help_msg = 'Publish your click app to the OpenStore'

        self.api_key = None
        self.changelog = ''
        self.timeout = 60
        self.connect_timeout = 5

    def setup_parser(self, parser):
        parser.add_argument(
            '--apikey',
            help='Api key for the OpenStore',
        )
        parser.add_argument(
            '--timeout',
            default=self.timeout,
            type=int,
            help='Timeout in seconds on upload',
        )
        parser.add_argument(
            'changelog',
            nargs='*',
            help='Change log message to be appended in OpenStore app changelog '
            '(prepend with a -- to make sure Clickable does not interpret part '
            'of the changelog)',
        )

    def configure(self, args):
        self.api_key = args.apikey
        self.changelog = ' '.join(args.changelog)
        self.timeout = args.timeout

        self.parse_env()

    def configure_nested(self):
        self.parse_env()

    def parse_env(self):
        if not self.api_key:
            self.api_key = env('OPENSTORE_API_KEY')

    def determine_channel(self):
        if '16.04' in self.config.framework:
            return 'xenial'
        if '20.04' in self.config.framework:
            return 'focal'
        raise ClickableException(f'Clickable does not know an Open Store channel \
                corresponding to framework {self.config.framework}')

    def run(self):
        if not REQUESTS_AVAILABLE:
            raise ClickableException(
                'Unable to publish app, python requests module is not installed'
            )

        if not self.api_key:
            raise ClickableException('No api key specified, use OPENSTORE_API_KEY or --apikey')

        click = self.config.install_files.get_click_filename()
        click_path = os.path.join(self.config.build_dir, click)

        url = OPENSTORE_API
        if 'OPENSTORE_API' in os.environ and os.environ['OPENSTORE_API']:
            url = os.environ['OPENSTORE_API']

        package_name = self.config.install_files.find_package_name()
        url = url + OPENSTORE_API_PATH.format(package_name)
        channel = self.determine_channel()
        files = {'file': open(click_path, 'rb')}
        data = {
            'channel': channel,
            'changelog': self.changelog.encode('utf8', 'surrogateescape'),
        }
        params = {'apikey': self.api_key}

        logger.info('Uploading version %s of %s for %s/%s to the OpenStore',
                    self.config.install_files.find_version(),
                    package_name,
                    channel,
                    self.config.arch)
        try:
            response = requests.post(url, files=files, data=data, params=params,
                                     timeout=(self.connect_timeout, self.timeout))
        except (ReadTimeout, TimeoutError) as e:
            raise ClickableException(
                "Upload timed out. Consider setting a higher timeout via --timeout argument."
            ) from e
        except (ConnectTimeout) as e:
            raise ClickableException(
                "Couldn't connect to the server. Check your internet connection.") from e
        except (requests.exceptions.ConnectionError) as e:
            raise ClickableException("Connection to the server died.") from e

        if response.status_code == 200:
            logger.info('Upload successful')
        elif response.status_code == 404:
            title = urllib.parse.quote(self.config.install_files.find_package_title())
            raise ClickableException(
                'App needs to be created in the OpenStore before you can publish it. '
                f'Visit {OPENSTORE_API}/submit?appId={package_name}&name={title}'
            )
        else:
            try:
                message = response.json()['message']
            except Exception:  # pylint: disable=broad-except
                message = response.text

            raise ClickableException(
                f'Failed to upload click: {message} ({response.status_code})'
            )
