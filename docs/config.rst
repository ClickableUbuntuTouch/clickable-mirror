.. _config:

Clickable Config Format
=======================

Optionally, a config file can be provided to configure Clickable for
all projects. The file needs to be located at ``~/.clickable/config.yaml``.

Example:

.. code-block:: javascript

    device:
      ipv4: 192.168.178.41

    build:
      skip_review: true
      default_arch: arm64

    cli:
      default_chain:
        - build
        - install
        - launch
        - logs
      scripts:
        submodules: git submodule update --init --recursive

    ide:
      image_setup:
        run:
          - apt update
          - apt install vim -y

      default: vim .

device
------

Default configurations for the target device.

.. _ipv4:

ipv4
^^^^

IP address used for connecting via SSH.

Can be overwritten on command line with ``--ssh``.

serial_number
^^^^^^^^^^^^^

Device serial number for connecting via ADB.

Can be overwritten on command line with ``--serial-number``.

.. _default_target:

default_target
^^^^^^^^^^^^^^

Target device used by default. Allowed values are ``ssh``, ``adb``, ``host``
and ``detect`` (default value).

====== =================
Value  Description
====== =================
host   Don't detect remote devices and interact with host system instead.
detect Try to detect a remote device (default behavior)
ssh    Check via SSH before checking for ADB devices (currently default behavior).
adb    Check for ADB devices before checking via SSH.
====== =================

always_detect
^^^^^^^^^^^^^

Detect the remote device and its architecture even for commands that don't require
a connection to the device (e.g. ``build``). Behaves like ``--arch detect``

skip_uninstall
^^^^^^^^^^^^^^

Skip uninstall step before installing an app.

Can be overwritten on command line with ``install --skip-uninstall``.


build
-----

Default configuration for the ``build`` command.

always_clean
^^^^^^^^^^^^

Always clean the build directory before building.

skip_review
^^^^^^^^^^^

Skip automatic review after building. Review can still be executed manually
using the ``review`` command.

default_arch
^^^^^^^^^^^^

Target architecture used by default.

Can be overwritten on command line with ``--arch``.
Allowed values are ``armhf``, ``arm64``, ``amd64`` and ``detect``.


environment
-----------

Default configuration for the environment Clickable is running in.

nvida
^^^^^

Set to ``"on"`` if you use the proprietary nvidia driver in order to use a special
docker image with an nvidia workaround in Desktop Mode.
Set to ``"off"`` to disable nvidia support.
Set to ``"auto"`` to let Clickable automatically detect whether an nvidia driver is in
use. This is the default behavior.

non_interactive
^^^^^^^^^^^^^^^

Do not show prompts for anything.

container_mode
^^^^^^^^^^^^^^

Run all commands withing the environment and do not use docker containers.

restrict_arch
^^^^^^^^^^^^^

Restrict the architecture the environment can build for. This is meant to be used
in conjunction with ``container_mode``.
Allowed values are ``armhf``, ``arm64``, ``amd64`` and ``host``.

cli
---

default_chain
^^^^^^^^^^^^^

Change the default chain of commands to be executed on a pure ``clickable`` or a
``clickable chain`` call.

scripts
^^^^^^^

Add scripts to be used with the ``script`` command.

ide
---

image_setup
^^^^^^^^^^^

Additional run commands and env vars for preparing the ``ide`` docker image. This
allows to install your preferred IDE.

default
^^^^^^^

Default run command for ``ide`` command. This allows to start your preferred IDE
by default.
