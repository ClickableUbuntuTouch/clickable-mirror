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
    GO = 'go'
    RUST = 'rust'
    PRECOMPILED = 'precompiled'

    project_config_path_options = [
        "clickable.yaml",
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
        GO,
        RUST,
        PRECOMPILED
    ]
    arch_agnostic_builders = [PURE_QML_QMAKE, PURE_QML_CMAKE, PURE]

    container_mapping = {
        "armhf": {
            ('16.04.4', 'armhf'): 'clickable/armhf-16.04-armhf:16.04.4-qt5.9',
            ('16.04.5', 'armhf'): 'clickable/armhf-16.04-armhf:16.04.5',
        },
        "arm64": {
            ('16.04.4', 'arm64'): 'clickable/arm64-16.04-arm64:16.04.4-qt5.9',
            ('16.04.5', 'arm64'): 'clickable/arm64-16.04-arm64:16.04.5',
        },
        "amd64": {
            ('16.04.4', 'armhf'): 'clickable/amd64-16.04-armhf:16.04.4-qt5.9',
            ('16.04.4', 'arm64'): 'clickable/amd64-16.04-arm64:16.04.4-qt5.9',
            ('16.04.4', 'amd64'): 'clickable/amd64-16.04-amd64:16.04.4-qt5.9',
            ('16.04.4', 'amd64-nvidia'): 'clickable/amd64-16.04-amd64-nvidia:16.04.4-qt5.9',
            ('16.04.4', 'amd64-ide'): 'clickable/amd64-16.04-amd64-ide:16.04.4-qt5.9',
            ('16.04.4', 'amd64-nvidia-ide'):
                'clickable/amd64-16.04-amd64-nvidia-ide:16.04.4-qt5.9',
            ('16.04.5', 'armhf'): 'clickable/amd64-16.04-armhf:16.04.5',
            ('16.04.5', 'arm64'): 'clickable/amd64-16.04-arm64:16.04.5',
            ('16.04.5', 'amd64'): 'clickable/amd64-16.04-amd64:16.04.5',
            ('16.04.5', 'amd64-nvidia'): 'clickable/amd64-16.04-amd64-nvidia:16.04.5',
            ('16.04.5', 'amd64-ide'): 'clickable/amd64-16.04-amd64-ide:16.04.5',
            ('16.04.5', 'amd64-nvidia-ide'): 'clickable/amd64-16.04-amd64-nvidia-ide:16.04.5',
        }
    }

    framework_image_mapping = {
        "ubuntu-sdk-16.04": "16.04.4",
        "ubuntu-sdk-16.04.1": "16.04.4",
        "ubuntu-sdk-16.04.2": "16.04.4",
        "ubuntu-sdk-16.04.3": "16.04.4",
        "ubuntu-sdk-16.04.4": "16.04.4",
        "ubuntu-sdk-16.04.5": "16.04.5",
    }

    framework_fallback = "16.04.5"

    default_qt_framework_mapping = {
        '5.9': 'ubuntu-sdk-16.04.4',
        '5.12': 'ubuntu-sdk-16.04.5',
    }

    default_qt = '5.12'

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
        'aarch64': 'arm64',  # Linux reports aarch64
        'arm64': 'arm64',  # Mac reports arm64
        'armv7l': 'armhf',
    }
    host_arch = host_arch_mapping.get(platform.machine(), None)

    clickable_dir = os.path.expanduser('~/.clickable')
    clickable_config_path = os.path.join(clickable_dir, 'config.yaml')
    desktop_device_home = os.path.join(clickable_dir, 'home')
    device_home = '/home/phablet'
