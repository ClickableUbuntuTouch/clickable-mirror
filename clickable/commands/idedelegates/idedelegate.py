from clickable.utils import let_user_confirm


class IdeCommandDelegate:
    def __init__(self, config):
        self.config = config

    def override_command(self, path):
        pass

    def before_run(self, config, docker_config):
        pass

    def confirm(self, message, default=True):
        if not self.config.interactive:
            return True

        return let_user_confirm(message, default)
