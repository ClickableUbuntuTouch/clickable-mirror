.. _commands:

Commands
========

``clickable`` is the main command. Run it from somewhere within the directory of your project. It can be combined with multiple sub-commands. This documentation does not list all subcommands or parameters. Only some of the most common ones are explained below. Run ``clickable --help`` to list them all. ``clickable <subcommand> --help`` explains a single command in detail.

Important:
1. Parameters for subcommands need to be placed AFTER the subcommand!
2. Parameters for one subcommand may not necessarily be available for other subcommands. Check with ``--help`` if not sure.

``clickable``
-------------

A pure ``clickable`` call is equivalent to ``clickable chain``.

``clickable chain``
-------------------

Chains multiple commands that can be specified. The default chain can be configured via the
:ref:`default <project-config-default>` field. The default chain itself defaults to
``build install launch``.

A clean build can be enforced by running ``clickable chain --clean``.

``clickable desktop``
---------------------

Compile and run the app on the desktop. Accepts the same arguments as the ``build`` command plus
some desktop mode specific ones.

Note: ArchLinux user might need to run ``xhost +local:clickable`` before using
desktop mode.

Run ``clickable desktop --verbose`` to show the executed docker command.

Run ``clickable desktop --dark-mode`` to set the dark mode preference.

Run ``clickable desktop --lang <language code>_<country code>`` (for example, `fr_FR`) to test using a different language.

The env var ``CLICKABLE_DESKTOP_MODE`` is set in desktop mode.

.. _nvidia:

``clickable desktop --nvidia``
------------------------------

``clickable`` checks automatically if nvidia-drivers are installed and turns on nvidia
mode. If ``prime-select`` is installed, it is queried to check whether the nvidia-driver
is actually in use.
The ``--nvidia`` flag lets you manually enforce nvidia mode. The ``--no-nvidia``
flag in contrast lets you disable automatic detection.

Depending on your docker version, the docker execution will change and
you need to provide additional system requirements:

**docker < 19.03 system requirements**

* nvidia-modprobe
* nvidia-docker

On Ubuntu, install these requirements using ``apt install nvidia-modprobe nvidia-docker``.

**docker >= 19.03 system requirements**

* nvidia-container-toolkit

On Ubuntu, install these requirements using ``apt install nvidia-container-toolkit``.

To be able to install the nvidia-container-toolkit you have to perform the following commands
(as mentioned on https://www.server-world.info/en/note?os=Ubuntu_20.04&p=nvidia&f=2):

As root:

.. code-block:: bash

   curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | apt-key add -

   curl -s -L https://nvidia.github.io/nvidia-docker/ubuntu20.04/nvidia-docker.list > /etc/apt/sources.list.d/nvidia-docker.list

   apt update

   apt -y install nvidia-container-toolkit

   systemctl restart docker

Run clickable with the ``--verbose`` flag to see the executed command for your system.

.. _commands-ide:

``clickable ide <custom_command>``
----------------------------------

Will run ``custom_command`` inside ide container wrapper.
e.g. Launch qtcreator: ``clickable ide qtcreator``.


``clickable ci <custom_command>``
---------------------------------

Will run ``custom_command`` inside a Clickable CI container.

``clickable create``
--------------------

Generate a new app from a list of :ref:`app template options <app-templates>`.

``clickable create <app template name>``

Generate a new app from an :ref:`app template <app-templates>` by name.

``clickable shell``
-------------------

Opens a shell on the device via ssh. This is similar to the ``phablet-shell`` command.

``clickable clean``
-------------------

Cleans out the app build dir. Can by applied to libraries by appending ``--libs``.

``clickable build``
-------------------

Builds the project using the specified builder, build dir, and build commands.
Then it takes the built files and compiles them into a click package (you can
find it in the build dir).

Set the manifest architecture field to ``@CLICK_ARCH@`` and the framework field
to ``@CLICK_FRAMEWORK@`` to have Clickable replace them with the appropriate values.

``clickable build --libs``
--------------------------

Builds libraries specified in the project config.

``clickable build --output=/path/to/some/diretory``
---------------------------------------------------

Takes the built files and compiles them into a click package, outputting the
compiled click to the directory specified by ``--output``.

``clickable review``
--------------------

Takes the built click package and runs click-review against it. This allows you
to review your click without installing click-review on your computer.

.. _commands-test:

``clickable test``
------------------

Run your test suite in with a virtual screen. By default this runs qmltestrunner,
but you can specify a custom command by setting the :ref:`test <project-config-test>`
property in your project config.

``clickable install``
---------------------

Takes a built click package and installs it on a device.

``clickable install ./path/to/click/app.click``

Installs the specified click package on the device

``clickable launch``
--------------------

Launches the app on a device.

``clickable launch <app name>``

Launches the specified app on a device.

``clickable logs``
------------------

Follow the apps log file on the device.

``clickable log``
------------------

Dumps the apps log file on the device.

``clickable publish``
---------------------

Publish your click app to the OpenStore. Check the
:ref:`Getting started doc <getting-started>` for more info.

``clickable publish "changelog message"``

Publish your click app to the OpenStore with a message to add to the changelog.

``clickable run "some command"``
--------------------------------

Runs an arbitrary command in the clickable container. Changes do not persist.
This is only meant to inspect the container. Opens a root bash shell if no
command is specified.

``clickable update-images``
---------------------------

Update the docker images for use with clickable.

``clickable no-lock``
---------------------

Turns off the display timeout for a connected device.

``clickable writable-image``
----------------------------

Make your Ubuntu Touch device's rootfs writable. This replaces to old
``phablet-config writable-image`` command.

``clickable devices``
---------------------

Lists the serial numbers and model names for attached devices. Useful when
multiple devices are attached and you need to know what to use for the ``-s``
argument.

``clickable script <custom command>``
-------------------------------------

Runs a custom command specified in the "scripts" config

.. _container-mode:

``clickable <any command> --container-mode``
--------------------------------------------

Runs all builds commands on the current machine and not in a container. This is
useful from running clickable from within a container.

``clickable <any command> --verbose``
-------------------------------------

Have Clickable print out debug information about whatever command(s) are being run.

``clickable <any command> --ssh <ip address>``
----------------------------------------------

Run a command with a device over ssh rather than the default adb.
