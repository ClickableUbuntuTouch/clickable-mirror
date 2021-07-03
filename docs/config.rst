.. _config:

Clickable Config Format
=======================

Optionally, a config file can be provided to configure Clickable for
all projects. The file needs to be located at ``~/.clickable/config.yaml``.

Example:

.. code-block:: javascript

    device:
      ipv4: 192.168.178.41
      arch: arm64

    build:
      skip_review: true

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

ipv4
^^^^

IP address used for connecting via SSH.

Can be overwritten on command line with ``--ssh``.

serial_number
^^^^^^^^^^^^^

Device serial number for connecting via ADB. 

Can be overwritten on command line with ``--serial-number``.

arch
^^^^

Target architecture used by default.

Can be overwritten on command line with ``--arch``.

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
