import os
from datetime import datetime

from clickable.config.constants import Constants
from clickable.exceptions import ClickableException
from clickable.utils import check_command
from .base import Command

COOKIECUTTER_AVAILABLE = True
try:
    import cookiecutter.main
except ImportError:
    COOKIECUTTER_AVAILABLE = False


COOKIECUTTER_URL = 'https://gitlab.com/clickable/ut-app-meta-template.git'


TEMPLATE_MAP = {
    'pure-qml-cmake': 'QML Only',
    'cmake': 'C++',
    'python-cmake': 'Python',
    'html': 'HTML',
    'go': 'Go',
    'rust': 'Rust',
    'godot': 'Godot (Precompiled)',
}

LICENSE_MAP = {
    'gpl3': 'GNU General Public License v3',
    'mit': 'MIT license',
    'bsd': 'BSD license',
    'isc': 'ISC license',
    'apache': 'Apache Software License 2.0',
    'proprietary': 'Not open source',
}


class CreateCommand(Command):
    def __init__(self):
        Command.__init__(self)
        self.cli_conf.aliases = ['init']
        self.cli_conf.name = 'create'
        self.cli_conf.help_msg = 'Generate a new app from a list of app template options'

        self.extra_context = {}
        self.extra_context['Copyright Year'] = datetime.now().year
        self.output_dir = '.'

    def setup_parser(self, parser):
        parser.add_argument(
            '--title',
            metavar='"App Title"',
            default=None,
            help='The app title as displayed to the user',
        )
        parser.add_argument(
            '--name',
            metavar='appname',
            default=None,
            help='Set the app name which is used in the manifest',
        )
        parser.add_argument(
            '--namespace',
            metavar='yourname',
            default=None,
            help='Namespace of the author which is used in the manifest',
        )
        parser.add_argument(
            '--description',
            metavar='"A short description of your app"',
            default=None,
            help='App description which is used in the manifest',
        )
        parser.add_argument(
            '--maintainer',
            metavar='"Your Full Name"',
            default=None,
            help='Maintainer name which is used in the manifest',
        )
        parser.add_argument(
            '--mail',
            metavar='email@domain.org',
            default=None,
            help='Maintainer e-mail address which is used in the manifest',
        )
        parser.add_argument(
            '--template',
            default=None,
            choices=TEMPLATE_MAP.keys(),
            help='One of the app templates provided by Clickable',
        )
        parser.add_argument(
            '--license',
            default=None,
            choices=LICENSE_MAP.keys(),
            help='License used in the source files and README',
        )
        year_now = self.extra_context['Copyright Year']
        parser.add_argument(
            '--copyright-year',
            default=year_now,
            metavar=year_now,
            help='Copyright year used in license files',
        )
        parser.add_argument(
            '--git-tag-versioning',
            action='store_true',
            help='Confige CMake to dynamically set app versions based on git tags',
        )
        parser.add_argument(
            '--dir',
            default=self.output_dir,
            help='Output directory under which the project directory is created',
        )

    def configure(self, args):
        self.output_dir = args.dir
        self.extra_context['Copyright Year'] = args.copyright_year

        if args.name:
            self.extra_context['App Name'] = args.name

        if args.namespace:
            self.extra_context['Namespace'] = args.namespace

        if args.title:
            self.extra_context['Title'] = args.title

        if args.description:
            self.extra_context['Description'] = args.description

        if args.maintainer:
            self.extra_context['Maintainer Name'] = args.maintainer

        if args.mail:
            self.extra_context['Maintainer Email'] = args.mail

        if args.template:
            self.extra_context['Template'] = TEMPLATE_MAP[args.template]

        if args.license:
            self.extra_context['License'] = LICENSE_MAP[args.license]

        if args.git_tag_versioning:
            self.extra_context['Git Tag Versioning'] = 'y'

    def run(self):
        if not COOKIECUTTER_AVAILABLE:
            raise ClickableException(
                'Cookiecutter is not available on your computer, more information '
                'can be found here: '
                'https://cookiecutter.readthedocs.io/en/latest/installation.html'
            )

        check_command("git")

        config_file = os.path.join(Constants.clickable_dir, 'cookiecutter_config.yaml')
        if not os.path.isfile(config_file):
            config_file = None

        try:
            cookiecutter.main.cookiecutter(
                COOKIECUTTER_URL,
                extra_context=self.extra_context,
                no_input=not self.config.interactive,
                config_file=config_file,
                output_dir=self.output_dir,
            )
        except cookiecutter.exceptions.FailedHookException as err:
            raise ClickableException('Failed to create app, see logs above') from err
