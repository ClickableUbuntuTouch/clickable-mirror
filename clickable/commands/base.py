from clickable.exceptions import ClickableException
from clickable.config.global_config import GlobalConfig
from clickable.config.device import DeviceConfig
from clickable.device import Device
from clickable.container import Container
from clickable.config.project import ProjectConfig
from clickable.config.command import CommandConf, CommandCliConf
from clickable.utils import let_user_confirm


class Command():
    def __init__(self):
        self.device = None
        self.container = None
        self.config = None
        self.cli_conf = CommandCliConf()
        self.command_conf = CommandConf()
        self.global_config = None

    def init_from_command(self, command):
        self.config = command.config
        self.device = command.device
        self.container = command.container
        self.configure_nested()

    def parse_common_options(self, args):
        self.load_configs(args)
        self.create_device(args)

        device_arch = self.device.device_arch if self.device else None
        commands = [args.sub_command]
        self.config.configure(self.global_config, commands, args, device_arch=device_arch)

    def load_configs(self, args):
        self.global_config = GlobalConfig(args.clickable_config)
        self.config = ProjectConfig(args.config)

    def create_device(self, args):
        device_args = args if self.command_conf.device_command else None
        device_required_pre = self.command_conf.device_command or args.arch == 'detect'
        device_config = DeviceConfig(self.global_config.device.config, device_args,
                                     device_required_pre)

        may_use = self.command_conf.build_command and \
            self.global_config.build.default_arch == 'detect'
        if device_config.required or may_use:
            self.device = Device(device_config)

    def check_errors(self):
        if (self.command_conf.device_command and self.command_conf.arch_specific
                and self.config.arch != "all" and self.config.arch != self.device.device_arch):
            raise ClickableException(
                f'The device architecture {self.device.device_arch} does not match '
                f'the configured architecture {self.config.arch}.')

    def start(self, args):
        self.parse_common_options(args)

        self.setup()
        self.configure(args)
        self.check_errors()
        self.run()

    def setup(self):
        self.container = Container(self.config)

    def confirm(self, message, default=True):
        """ Let user confirm an action. Returns default in non-interactive mode. """
        if not self.config.interactive:
            return default

        return let_user_confirm(message, default)

    def setup_complete_parser(self, parser):
        if self.command_conf.device_command:
            DeviceConfig.setup_parser(parser)

        self.setup_parser(parser)

    def setup_parser(self, parser):
        """ Set up command specific command line interface """
        # Implemented in subclasses

    def configure(self, args):
        """ Configure from command line interface with arguments """
        # Implemented in subclasses

    def configure_nested(self):
        """ Configure as nested command, e.g. when running chained """
        # Implemented in subclasses

    def run(self):
        """ Run command """
        raise NotImplementedError('run is not yet implemented')
