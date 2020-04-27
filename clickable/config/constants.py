import os

class Constants(object):
    PURE_QML_QMAKE = 'pure-qml-qmake'
    QMAKE = 'qmake'
    PURE_QML_CMAKE = 'pure-qml-cmake'
    CMAKE = 'cmake'
    CUSTOM = 'custom'
    CORDOVA = 'cordova'
    PURE = 'pure'
    PYTHON = 'python'
    GO = 'go'
    RUST = 'rust'
    PRECOMPILED = 'precompiled'

    builders = [PURE_QML_QMAKE, QMAKE, PURE_QML_CMAKE, CMAKE, CUSTOM, CORDOVA, PURE, PYTHON, GO, RUST, PRECOMPILED]
    arch_agnostic_builders = [PURE_QML_QMAKE, PURE_QML_CMAKE, PURE]

    container_mapping = {
        "x86_64": {
            ('16.04', 'armhf'): 'clickable/ubuntu-sdk:16.04-armhf',
            ('16.04', 'amd64'): 'clickable/ubuntu-sdk:16.04-amd64',
            ('16.04', 'amd64-nvidia'): 'clickable/ubuntu-sdk:16.04-amd64-nvidia',
            ('16.04', 'arm64'): 'clickable/ubuntu-sdk:16.04-arm64',
        }
    }

    arch_triplet_mapping = {
        'armhf': 'arm-linux-gnueabihf',
        'arm64': 'aarch64-linux-gnu',
        'amd64': 'x86_64-linux-gnu',
        'all': 'all'
    }

    host_arch_mapping = {
        'x86_64': 'amd64',
        'aarch64': 'arm64',
        'armv7l': 'armhf',
    }

    desktop_device_home = os.path.expanduser('~/.clickable/home')
    device_home = '/home/phablet'