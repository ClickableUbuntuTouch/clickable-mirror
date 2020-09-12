class Builder(object):
    name = None

    def __init__(self, config, container, debug_build):
        self.config = config
        self.container = container
        self.debug_build = debug_build

    def build(self):
        raise NotImplementedError()
