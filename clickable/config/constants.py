import os
import platform


class Constants():
    PURE_QML_QMAKE = 'pure-qml-qmake'
    QMAKE = 'qmake'
    PURE_QML_CMAKE = 'pure-qml-cmake'
    CMAKE = 'cmake'
    CUSTOM = 'custom'
    PURE = 'pure'
    QBS = 'qbs'
    GO = 'go'
    RUST = 'rust'
    PRECOMPILED = 'precompiled'

    project_config_path_options = [
        "clickable.yaml",
        "clickable.yml",
        "clickable.json"
    ]

    builders = [
        PURE_QML_QMAKE,
        QMAKE,
        PURE_QML_CMAKE,
        CMAKE,
        CUSTOM,
        PURE,
        QBS,
        GO,
        RUST,
        PRECOMPILED
    ]
    arch_agnostic_builders = [PURE_QML_QMAKE, PURE_QML_CMAKE, PURE]

    docker_registry = os.environ.get(
        'CLICKABLE_DOCKER_REGISTRY',
        'docker.io'
    )

    container_mapping = {
        "armhf": {
            ('16.04.5', 'armhf'):
                os.path.join(docker_registry, 'clickable/armhf-16.04-armhf:16.04.5'),
        },
        "arm64": {
            ('16.04.5', 'arm64'):
                os.path.join(docker_registry, 'clickable/arm64-16.04-arm64:16.04.5'),
            ('20.04', 'arm64'):
                os.path.join(docker_registry, 'clickable/arm64-20.04-arm64'),
            ('24.04-1.x', 'arm64'):
                os.path.join(docker_registry, 'clickable/arm64-24.04-1.x-arm64'),
            ('next', 'arm64'):
                os.path.join(docker_registry, 'clickable/arm64-utnext-arm64'),
        },
        "amd64": {
            ('16.04.5', 'armhf'):
                os.path.join(docker_registry, 'clickable/amd64-16.04-armhf:16.04.5'),
            ('16.04.5', 'arm64'):
                os.path.join(docker_registry, 'clickable/amd64-16.04-arm64:16.04.5'),
            ('16.04.5', 'amd64'):
                os.path.join(docker_registry, 'clickable/amd64-16.04-amd64:16.04.5'),
            ('16.04.5', 'amd64-nvidia'):
                os.path.join(docker_registry, 'clickable/amd64-16.04-amd64-nvidia:16.04.5'),
            ('16.04.5', 'amd64-ide'):
                os.path.join(docker_registry, 'clickable/amd64-16.04-amd64-ide:16.04.5'),
            ('16.04.5', 'amd64-nvidia-ide'):
                os.path.join(docker_registry, 'clickable/amd64-16.04-amd64-nvidia-ide:16.04.5'),
            ('20.04', 'amd64'):
                os.path.join(docker_registry, 'clickable/amd64-20.04-amd64'),
            ('20.04', 'armhf'):
                os.path.join(docker_registry, 'clickable/amd64-20.04-armhf'),
            ('20.04', 'arm64'):
                os.path.join(docker_registry, 'clickable/amd64-20.04-arm64'),
            ('20.04', 'amd64-nvidia'):
                os.path.join(docker_registry, 'clickable/amd64-20.04-amd64-nvidia'),
            ('20.04', 'amd64-ide'):
                os.path.join(docker_registry, 'clickable/amd64-20.04-amd64-ide'),
            ('20.04', 'amd64-nvidia-ide'):
                os.path.join(docker_registry, 'clickable/amd64-20.04-amd64-nvidia-ide'),
            ('24.04-1.x', 'amd64'):
                os.path.join(docker_registry, 'clickable/amd64-24.04-1.x-amd64'),
            ('24.04-1.x', 'armhf'):
                os.path.join(docker_registry, 'clickable/amd64-24.04-1.x-armhf'),
            ('24.04-1.x', 'arm64'):
                os.path.join(docker_registry, 'clickable/amd64-24.04-1.x-arm64'),
            ('24.04-1.x', 'amd64-nvidia'):
                os.path.join(docker_registry, 'clickable/amd64-24.04-1.x-amd64-nvidia'),
            ('24.04-1.x', 'amd64-ide'):
                os.path.join(docker_registry, 'clickable/amd64-24.04-1.x-amd64-ide'),
            ('24.04-1.x', 'amd64-nvidia-ide'):
                os.path.join(docker_registry, 'clickable/amd64-24.04-1.x-amd64-nvidia-ide'),
            # (amd64-utnext-[ARCH]).
            ('next', 'amd64'):
                os.path.join(docker_registry, 'clickable/amd64-utnext-amd64'),
            ('next', 'armhf'):
                os.path.join(docker_registry, 'clickable/amd64-utnext-armhf'),
            ('next', 'arm64'):
                os.path.join(docker_registry, 'clickable/amd64-utnext-arm64'),
            ('next', 'amd64-nvidia'):
                os.path.join(docker_registry, 'clickable/amd64-utnext-amd64-nvidia'),
            ('next', 'amd64-ide'):
                os.path.join(docker_registry, 'clickable/amd64-utnext-amd64-ide'),
            ('next', 'amd64-nvidia-ide'):
                os.path.join(docker_registry, 'clickable/amd64-utnext-amd64-nvidia-ide'),
        }
    }

    ci_container_mapping = {
        ('16.04.5', 'armhf'): os.path.join(docker_registry, 'clickable/ci-16.04-armhf'),
        ('16.04.5', 'arm64'): os.path.join(docker_registry, 'clickable/ci-16.04-arm64'),
        ('16.04.5', 'amd64'): os.path.join(docker_registry, 'clickable/ci-16.04-amd64'),
        ('20.04', 'amd64'): os.path.join(docker_registry, 'clickable/ci-20.04-amd64'),
        ('20.04', 'armhf'): os.path.join(docker_registry, 'clickable/ci-20.04-armhf'),
        ('20.04', 'arm64'): os.path.join(docker_registry, 'clickable/ci-20.04-arm64'),
        ('24.04-1.x', 'amd64'): os.path.join(docker_registry, 'clickable/ci-24.04-1.x-amd64'),
        ('24.04-1.x', 'armhf'): os.path.join(docker_registry, 'clickable/ci-24.04-1.x-armhf'),
        ('24.04-1.x', 'arm64'): os.path.join(docker_registry, 'clickable/ci-24.04-1.x-arm64'),
        ('next', 'amd64'): os.path.join(docker_registry, 'clickable/ci-utnext-amd64'),
        ('next', 'armhf'): os.path.join(docker_registry, 'clickable/ci-utnext-armhf'),
        ('next', 'arm64'): os.path.join(docker_registry, 'clickable/ci-utnext-arm64'),
    }

    framework_image_mapping = {
        "ubuntu-sdk-16.04": "16.04.5",
        "ubuntu-sdk-20.04": "20.04",
        "ubuntu-sdk-20.04.1": "20.04",
        "ubuntu-touch-24.04-1.x": "24.04-1.x",
        "ubuntu-touch-next-internal": "next",
    }
    framework_image_fallback = {
        '16.04': '16.04.5',
        '20.04': '20.04',
        '24.04-1.x': '24.04-1.x',
        'next': 'next',
    }

    default_qt_framework_mapping = {
        '5.12': 'ubuntu-sdk-20.04.1',
        '5.15': 'ubuntu-touch-24.04-1.x',
    }

    default_qt = '5.12'

    framework_base = [
        '16.04',
        '20.04',
        '24.04-1.x',
        'next',
    ]
    framework_base_default = '20.04'

    arch_triplet_mapping = {
        'armhf': 'arm-linux-gnueabihf',
        'arm64': 'aarch64-linux-gnu',
        'amd64': 'x86_64-linux-gnu',
        'all': 'all'
    }

    rust_arch_target_mapping = {
        'amd64': 'x86_64-unknown-linux-gnu',
        'armhf': 'armv7-unknown-linux-gnueabihf',
        'arm64': 'aarch64-unknown-linux-gnu',
    }

    host_arch_mapping = {
        'x86_64': 'amd64',
        'amd64': 'amd64',  # Windows
        'aarch64': 'arm64',  # Linux
        'arm64': 'arm64',  # Mac
        'armv7l': 'armhf',
    }
    host_arch = host_arch_mapping.get(platform.machine().lower(), None)
    host_arch_triplet = arch_triplet_mapping.get(host_arch, None)

    host_home = os.path.expanduser('~')
    clickable_dir = os.path.join(host_home, '.clickable')
    clickable_config_path = os.path.join(clickable_dir, 'config.yaml')
    desktop_device_home = os.path.join(clickable_dir, 'home')
    device_home = '/home/phablet'
