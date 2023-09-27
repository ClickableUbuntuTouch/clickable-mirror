class CommandCliConf():
    def __init__(self):
        self.name = ''
        self.aliases = []
        self.help_msg = ''


class CommandConf():
    def __init__(self):
        self.device_command = False
        self.arch_specific = False
        self.build_command = False
