.. _migration8:

Clickable 8 Migration
=====================

This guide describes the changes that come with Clickable 8 and how to migrate a
project from Clickable 7.

For migration from Clickable 6 to 7, see :ref:`Clickable 7 Migration <migration7>`.

Default Framework
-----------------

The default framework changed from ``ubuntu-sdk-16.04.5`` to ``ubuntu-sdk-20.04``.
If your app is made for Ubuntu Touch 16.04, you need to set the framework:

.. code-block:: yaml

    framework: ubuntu-sdk-16.04.5

Command Line Interface
----------------------

Until Clickable 7, all commands would accept ``--ssh`` and ``--serial-number`` as
arguments. Starting with Clickable 8, only device commands like ``install`` or
``launch`` accept these.

If you want to opt into architecture detection for architecture-specific, but
non-device commands, like ``build``, you can pass ``--arch detect``.

For device commands, you can specify the target device with ``--target``, which
can be one of ``ssh``, ``adb``, ``host`` and ``detect`` (resolves to either
``ssh`` or ``adb``).

Project Config
--------------

There are no changes in the project configuration file format, except for the
removal of the ``cordova`` builder.

Clickable Config
----------------

Since Clickable 7, the default architecture is the host one, meant to
facilitate the Desktop Mode Use Case, e.g. a seemless
``clickable build --libs``, followed by ``clickable desktop``. For testing
on an ``armhf`` or ``arm64`` device, the user needed to specify the
architecture, e.g. ``clickable build --all --arch arm64`` followed by
``clickable chain install launch logs --arch arm64``. Thanks to architecture
detection in Clickable 8, the latter would automatically set the correct
architecture and the ``--arch`` argument can be ommitted.
For the ``build`` command, the issue remains, because it is a non-device
command.

If you do not commonly use Desktop Mode, it might be more convenient for you
to enforce architecture detection via ``always_detect`` in the ``device``
section. This comes at the cost of failing commands, when no target device is
accessible. Another solution is to set the ``default_arch`` in the ``build``
section to your device's architecture.

Thanks to architecture detection, the ``arch`` parameter in the ``device``
section became superfluous and is deprecated and ignored in Clickable 8.

You can set a ``default_target`` in the ``device`` section. This way you can
control whether SSH or ADB takes precedence or you can set the ``host`` target
if you run Clickable inside an Ubuntu Touch environment.

NodeJS Removal
--------------

With the drop of Cordova support, nodejs was removed from the docker images
as well. If your app depends on it, you need to add it to your
``dependencies_host``. In order to get an up-to-date version of nodejs,
consider adding a repo via the ``image_setup`` field, e.g.:


.. code-block:: yaml

    image_setup:
      run:
      # Install instructions taken from https://github.com/nodesource/distributions#installation-instructions
      - mkdir -p /etc/apt/keyrings
      - curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg
      - echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_20.x nodistro main" | tee /etc/apt/sources.list.d/nodesource.list

    dependencies_host:
    - nodejs
