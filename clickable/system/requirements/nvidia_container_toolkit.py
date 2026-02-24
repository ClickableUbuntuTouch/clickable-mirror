from clickable.system.access import is_program_installed
from clickable.system.query import Query


class NvidiaContainerToolkit(Query):

    def is_met(self):
        return is_program_installed('nvidia-container-toolkit')

    def get_user_instructions(self):
        return ("You are running clickable in nvidia mode.\n"
                "Please install nvidia-container-toolkit.\n"
                "See the nvidia documentation for instructions: https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html\n")
