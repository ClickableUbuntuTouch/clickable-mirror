.. _commands:

Commands
========

The behavior of Clickable is controlled via commands, each with their own set of available
parameters.

.. code-block:: bash

   clickable <command> [param ...]

This documentation only lists some selected commands and parameters. Run
``clickable --help`` to see the list of all available commands and
``clickable <command> --help`` to get a command-specific help message listing its
available parameters.

Project-specific commands like ``build`` and ``install`` can be executed from the projec
root or any of its sub-directories, given there is a project config in the project root.

Running Clickable without a command is a shortcut to the default ``chain`` command (see
below). This special case allows a few universal parameters like ``--verbose`` and
``--arch``.

``chain``
---------

Chains multiple commands that can be specified. The default chain can be configured via the
:ref:`default <project-config-default>` field. If not configured, the default is
``build install launch``.

A clean build in a chain can be enforced by running ``clickable chain --clean``.

``desktop``
-----------

Compiles and runs the app on the desktop. Accepts the same arguments as the ``build`` command
plus some desktop mode specific ones.

Note: ArchLinux user might need to run ``xhost +local:clickable`` before using
desktop mode.

Run ``clickable desktop --dark-mode`` to set the dark mode preference.

Run ``clickable desktop --lang <language code>_<country code>`` (for example, `fr_FR`)
to test using a different language.

Run ``clickable desktop --gdb`` to start the app via GDB.

Run ``clickable desktop --qmllive`` on a QML only app enable QML live update when QML files are
changed.

The env var ``CLICKABLE_DESKTOP_MODE`` is set in desktop mode.

.. _commands-ide:

``ide``
-------

Will run an IDE inside the Clickable docker container, QtCreator by default.

``ci``
------

Will open a root bash inside a Clickable CI container that can be used to debug a CI job.

``run``
-------

Opens a bash inside the Clickable docker container to analyze the build environment.
This is only meant to inspect the container. Changes do not persist.

``clickable run -- <some command>`` runs an arbitrary command in the Clickable container.

``create``
----------

Generate a new app from a list of :ref:`app template options <app-templates>`.

``shell``
---------

Opens a SSH shell on a connected device either via SSH or ADB.

``clean``
---------

Cleans out the app build dir. Can be applied to libraries by appending ``--libs``.

``build``
---------

Builds the project using the specified builder, build dir, and build commands.
Then it takes the built files and compiles them into a click package (you can
find it in the build dir). Finally runs a review.

Set the manifest architecture field to ``@CLICK_ARCH@`` and the framework field
to ``@CLICK_FRAMEWORK@`` to have Clickable replace them with the appropriate values.

Specify where to put the compiled click by ``--output``.

Builds libraries specified in the project config using the ``libs`` parameter.

``review``
----------

Takes the built click package and runs click-review against it. This allows you
to review your click without installing click-review on your computer.

The review runs automatically after a ``build`` command.

.. _commands-test:

``test``
--------

Run your test suite with a virtual screen. By default this runs ``qmltestrunner``,
but you can specify a custom command by setting the :ref:`test <project-config-test>`
property in your project config.

``install``
-----------

Takes a built click package from the build dir and installs it on a connected device.

``launch``
----------

Launches the app on a connected device.

``clickable launch <app name>`` launches the specified app.

``logs``
--------

Follows the app log file on a connected device.

``log``
------------------

Prints the app log file from a connected device.

``publish``
-----------

Publish your click package to the OpenStore. Check the
:ref:`Getting started doc <getting-started>` for more info.

``clickable publish "changelog message"`` publishs your click app to the OpenStore
with a message prepended to the changelog.

``update-images``
-----------------

Update the docker images used with Clickable.

``no-lock``
-----------

Turns off the display timeout for a connected device.

``writable-image``
------------------

Make your Ubuntu Touch device's rootfs writable.

``devices``
-----------

Lists the serial numbers and model names for attached devices using ADB. Useful when
multiple devices are attached and you need to know what to use for the ``-s``
argument.

``script``
----------

``clickable script <script name>`` runs a custom command specified as a script in the
project config.

Shared Parameters
-----------------

Some parameters can be used with multiple commands. This sections explains some of them.

``--arch``
^^^^^^^^^^

Specifying the target architecture allows Clickable to select to appropriate
docker image, choose the build dir path and (cross-)compile the app correctly.

Defaults to the host architecture.

.. _nvidia:

``--nvidia``
^^^^^^^^^^^^

The ``desktop`` command checks automatically if nvidia-drivers are installed and turns on nvidia
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

Run Clickable with the ``--verbose`` flag to see the executed command for your system.


.. _container-mode:

``--container-mode``
^^^^^^^^^^^^^^^^^^^^

Runs all builds commands on the current machine and not in a container. This is
useful for running Clickable from within a container, especially in a CI.

``--verbose``
^^^^^^^^^^^^^

Have Clickable print out debug information and more detailed error messages. Also
makes tools like ``make`` or ``cargo`` more verbose.

``--ssh``
^^^^^^^^^

Specify an IP address to run a device-related command over SSH rather than the default
ADB.

