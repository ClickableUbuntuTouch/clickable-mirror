import os
import urllib.parse

requests_available = True
try:
    import requests
except ImportError:
    requests_available = False

from .base import Command
from clickable.logger import logger
from clickable.exceptions import ClickableException
from clickable.utils import env

OPENSTORE_API = 'https://open-store.io'
OPENSTORE_API_PATH = '/api/v3/manage/{}/revision'


class PublishCommand(Command):
    def __init__(self):
        super().__init__()
        self.cli_conf.name = 'publish'
        self.cli_conf.help_msg = 'Publish your click app to the OpenStore'

        self.api_key = None
        self.changelog = ''

    def setup_parser(self, parser):
        parser.add_argument(
            '--apikey',
            help='Api key for the OpenStore',
        )
        parser.add_argument(
            'changelog',
            nargs='*',
            help='Change log message to be appended in OpenStore app changelog',
        )

    def configure(self, args):
        self.api_key = args.apikey
        self.changelog = ' '.join(args.changelog)

        self.parse_env()

    def configure_nested(self):
        self.parse_env()

    def parse_env(self):
        if not self.api_key:
            self.api_key = env('OPENSTORE_API_KEY')

    def run(self):
        if not requests_available:
            raise ClickableException('Unable to publish app, python requests module is not installed')

        if not self.api_key:
            raise ClickableException('No api key specified, use OPENSTORE_API_KEY or --apikey')

        click = self.config.install_files.get_click_filename()
        click_path = os.path.join(self.config.build_dir, click)

        url = OPENSTORE_API
        if 'OPENSTORE_API' in os.environ and os.environ['OPENSTORE_API']:
            url = os.environ['OPENSTORE_API']

        package_name = self.config.install_files.find_package_name()
        url = url + OPENSTORE_API_PATH.format(package_name)
        channel = 'xenial'
        files = {'file': open(click_path, 'rb')}
        data = {
            'channel': channel,
            'changelog': self.changelog.encode('utf8', 'surrogateescape'),
        }
        params = {'apikey': self.api_key}

        logger.info('Uploading version {} of {} for {}/{} to the OpenStore'.format(
            self.config.install_files.find_version(),
            package_name,
            channel,
            self.config.arch,
        ))
        response = requests.post(url, files=files, data=data, params=params)
        if response.status_code == requests.codes.ok:
            logger.info('Upload successful')
        elif response.status_code == requests.codes.not_found:
            title = urllib.parse.quote(self.config.install_files.find_package_title())
            raise ClickableException(
                'App needs to be created in the OpenStore before you can publish it. Visit {}/submit?appId={}&name={}'.format(
                    OPENSTORE_API,
                    package_name,
                    title,
                )
            )
        else:
            try:
                message = response.json()['message']
            except:
                message = 'Unspecified Error'
                logger.debug("Publish failed with: {}".format(response.text))

            raise ClickableException('Failed to upload click: {} ({})'.format(message, response.status_code))
