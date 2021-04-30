from .idedelegate import IdeCommandDelegate


class AtomDelegate(IdeCommandDelegate):

    def override_command(self, path):
        # atom does not launch within the bash process, but starts a decoupled process,
        # making the bash command directly return causing clickable to close the docker container
        # to fix this it needs to be started with --wait parameter to wait for the process to
        # finish before it returns. This way the container keeps running as long as atom runs.
        return path.replace('atom', "atom --wait .")

    def before_run(self, config, docker_config):

        # delete conflicting env vars in some cases
        docker_config.environment.pop("INSTALL_DIR", None)
        docker_config.environment.pop("APP_DIR", None)
        docker_config.environment.pop("SRC_DIR", None)
