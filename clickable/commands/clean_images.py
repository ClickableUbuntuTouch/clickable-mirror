import re

from clickable.utils import (
    get_docker_command,
    image_based_on,
    image_exists,
    run_subprocess_check_call,
    run_subprocess_check_output,
)

from clickable.config.constants import Constants
from clickable.logger import logger
from .base import Command

IMAGE_FORMAT = r'clickable\/\w{5}-(?:ut|)\d\d\.\d\d(?:-\d\.\w|)-\w{5}'


class CleanImagesCommand(Command):
    def __init__(self):
        Command.__init__(self)
        self.cli_conf.name = 'clean-images'
        self.cli_conf.aliases = []
        self.cli_conf.help_msg = 'Deletes obsolete Clickable docker images or '\
            'all of them.'

        self.all = False

    def setup_parser(self, parser):
        parser.add_argument(
            '--all',
            action='store_true',
            help='Delete all Clickable project docker images (does not include base images)',
            default=False,
        )

    def configure(self, args):
        self.all = args.all

    def run(self):
        self.container.check_docker()
        docker_executable = get_docker_command()

        pattern_derived = re.compile(IMAGE_FORMAT + r'-\w{8}[-\w]+')

        query_args = 'images --format {{.Repository}}'
        images_raw = run_subprocess_check_output(f'{docker_executable} {query_args}').strip()
        images_all = pattern_derived.findall(images_raw)

        logger.info("%i Clickable docker images found in total", len(images_all))

        if self.all:
            images = images_all
        else:
            base_images = get_base_images(docker_executable)
            logger.info("Checking which images are obsolete. This may take a while...")
            images = [
                img for img in images_all if is_obsolete(
                    img, base_images, docker_executable)]
            if images:
                logger.info("Found %i outdated images", len(images))

        if not images:
            logger.info('No obsolete images found')
            return

        images_string = ' '.join(images)
        delete_command = f"{docker_executable} rmi {images_string}"

        if self.confirm("Delete images?"):
            run_subprocess_check_call(delete_command)
            prune_command = f"{docker_executable} system prune"
            logger.info(
                'Finished. You may run "%s" to free some space.',
                prune_command)

            if self.confirm(f'Run "{prune_command}" now?', default=False):
                run_subprocess_check_call(prune_command)
        else:
            logger.info("skipped")


def is_obsolete(img, base_images, docker_executable):
    return all(not is_based_on(img, base, docker_executable) for base in base_images)


def is_based_on(img, base, docker_executable):
    # The only reason for this wrapper around image_based_on is the performance
    # bonus from checking the name against the base name first

    (base_img, base_trunc) = base
    return img.startswith(base_trunc) and image_based_on(img, base_img, docker_executable)


def get_base_images(docker_executable=None) -> list[(str, str)]:
    """
    collects the base images, which usually should not be cleaned
    :param docker_executable: pre-calculated executable info to not recalculate it on every call
    :return: list of base images and their group name
    """
    pattern_base = re.compile(IMAGE_FORMAT)
    base_images = []
    for img in Constants.container_mapping[Constants.host_arch].values():
        if image_exists(img, docker_executable):
            img_match = pattern_base.search(img)
            if img_match is not None:
                base_images.append((img, img_match.group()))
    return base_images
