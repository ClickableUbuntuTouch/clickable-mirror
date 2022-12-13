import os
import platform


class Constants():
    PURE_QML_QMAKE = 'pure-qml-qmake'
    QMAKE = 'qmake'
    PURE_QML_CMAKE = 'pure-qml-cmake'
    CMAKE = 'cmake'
    CUSTOM = 'custom'
    CORDOVA = 'cordova'
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
        CORDOVA,
        PURE,
        QBS,
        GO,
        RUST,
        PRECOMPILED
    ]
    arch_agnostic_builders = [PURE_QML_QMAKE, PURE_QML_CMAKE, PURE]

    container_mapping = {
        "armhf": {
            ('16.04.5', 'armhf'): 'docker.io/clickable/armhf-16.04-armhf:16.04.5',
        },
        "arm64": {
            ('16.04.5', 'arm64'): 'docker.io/clickable/arm64-16.04-arm64:16.04.5',
            ('20.04', 'arm64'): 'docker.io/clickable/arm64-20.04-arm64',
        },
        "amd64": {
            ('16.04.5', 'armhf'): 'docker.io/clickable/amd64-16.04-armhf:16.04.5',
            ('16.04.5', 'arm64'): 'docker.io/clickable/amd64-16.04-arm64:16.04.5',
            ('16.04.5', 'amd64'): 'docker.io/clickable/amd64-16.04-amd64:16.04.5',
            ('16.04.5', 'amd64-nvidia'): 'docker.io/clickable/amd64-16.04-amd64-nvidia:16.04.5',
            ('16.04.5', 'amd64-ide'): 'docker.io/clickable/amd64-16.04-amd64-ide:16.04.5',
            ('16.04.5', 'amd64-nvidia-ide'):
                'docker.io/clickable/amd64-16.04-amd64-nvidia-ide:16.04.5',
            ('20.04', 'amd64'): 'docker.io/clickable/amd64-20.04-amd64',
            ('20.04', 'armhf'): 'docker.io/clickable/amd64-20.04-armhf',
            ('20.04', 'arm64'): 'docker.io/clickable/amd64-20.04-arm64',
            ('20.04', 'amd64-nvidia'): 'docker.io/clickable/amd64-20.04-amd64-nvidia',
            ('20.04', 'amd64-ide'): 'docker.io/clickable/amd64-20.04-amd64-ide',
            ('20.04', 'amd64-nvidia-ide'): 'docker.io/clickable/amd64-20.04-amd64-nvidia-ide',
        }
    }

    ci_container_mapping = {
        ('16.04.5', 'armhf'): 'docker.io/clickable/ci-16.04-armhf',
        ('16.04.5', 'arm64'): 'docker.io/clickable/ci-16.04-arm64',
        ('16.04.5', 'amd64'): 'docker.io/clickable/ci-16.04-amd64',
        ('20.04', 'amd64'): 'docker.io/clickable/ci-20.04-amd64',
        ('20.04', 'armhf'): 'docker.io/clickable/ci-20.04-armhf',
        ('20.04', 'arm64'): 'docker.io/clickable/ci-20.04-arm64',
    }

    framework_image_mapping = {
        "ubuntu-sdk-16.04": "16.04.5",
        "ubuntu-sdk-20.04": "20.04",
    }
    framework_image_fallback = {
        '16.04': '16.04.5',
        '20.04': '20.04',
    }

    default_qt_framework_mapping = {
        '5.12': 'ubuntu-sdk-16.04.5',
    }

    default_qt = '5.12'

    framework_base = [
        '16.04',
        '20.04',
    ]
    framework_base_default = '16.04'

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

    host_home = os.path.expanduser('~')
    clickable_dir = os.path.join(host_home, '.clickable')
    clickable_config_path = os.path.join(clickable_dir, 'config.yaml')
    desktop_device_home = os.path.join(clickable_dir, 'home')
    device_home = '/home/phablet'
