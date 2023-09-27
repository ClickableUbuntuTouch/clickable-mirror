.. _usage:

Usage
=====

Getting Started
---------------

At this point it is assumed that you have completed the :ref:`installation
process <install>`

To find out all supported command line arguments run ``clickable --help``.

You can get started with using Clickable with an existing Ubuntu Touch app.
You can use Clickable with apps generated from the old Ubuntu Touch SDK IDE
or you can start fresh by running ``clickable create`` which is outlined in more
detail on the previous :ref:`getting started <getting-started>` page.

To run the default set of commands, simply run ``clickable`` in the root
directory of your app's code. Clickable will attempt to auto detect which
:ref:`builder <builders>` is able to build your app.

Note: The first time you run ``clickable`` in your app directory,
it will download a new Docker container which is about 1GB in size - so
plan your time and data transfer environment accordingly. This will only happen
the first time you build your app for a specific architecture and when you run
``clickable update-images``.

Running the default commands will:

1) Build the app
2) Build the click package (can be found in the build directory)
3) Uninstall the app from your phone
4) Install the newly built app on your phone
5) Kill the app on the phone (if already running)
6) Launch the app on your phone

By default the device is accessed using ADB, see below if you want to use SSH)

Note: ensure your device is in `developer mode <http://docs.ubports.com/en/latest/userguide/advanceduse/adb.html?highlight=mode#enable-developer-mode>`__
for the app to be installed when using ADB or `enable ssh <http://docs.ubports.com/en/latest/userguide/advanceduse/ssh.html>`__
when using SSH.

Configuration
-------------
One can specify the path to a :ref:`project config file <project-config>`
with ``--config``. If not
specified, Clickable will look for an optional configuration file called
``clickable.yaml`` and then ``clickable.json`` in the current and all
parent directories.
If there is none, Clickable will
ask if it should attempt to detect the type of app and choose a fitting
:ref:`builder <builders>` with default configuration.

Device Access
-------------

Host Device
^^^^^^^^^^^

For Clickable running directly on a Ubuntu Touch system, the target device
can be set to ``host`` (:ref:`default_target <default_target>` or
``--target host``).

.. _device-detection:

Device Detection
^^^^^^^^^^^^^^^^

For commands accessing a target device, Clickable will try to detect
whether the device is connected via SSH or ADB and the device architecture
(``arm64``, ``amd64`` or ``armhf``). It will only check for SSH, if an IP
address or hostname was specified via ``--ssh`` or in the
:ref:`Clickable Configuration <ipv4>`. It will check SSH before ADB, unless
ADB was configured as :ref:`default_target <default_target>`.

Device detection does not consider ``host`` as a target.
Setting the (default) target to ``host`` disables the device detection.

.. _ssh:

Connecting to a device over SSH
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

By default the device is connected to via ADB.
If you want to access a device over SSH you need to either specify the device
IP address or hostname on the command line (ex: ``clickable logs --ssh 192.168.1.10`` ) or you
can use the ``CLICKABLE_SSH`` env var. Make sure to `enable ssh <http://docs.ubports.com/en/latest/userguide/advanceduse/ssh.html>`__
on your device for this to work.

.. _multiple-devices:

Multiple connected ADB devices
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

By default Clickable assumes that there is only one device connected to your
computer via ADB. If you have multiple devices attached to your computer you
can specify which device to install/launch/etc on by using the flag
``--serial-number`` or ``-s`` for short. You can get the serial number
by running ``clickable devices``.

App Manifest
------------

The ``architecture`` and ``framework`` fields in the ``manifest.json`` need to be set according
to the architecture the app is build for (``--arch``) and the minimum framework version it
requires, e.g. depending on the QT Version (:ref:`qt_version <project-config-qt_version>`).
To let Clickable automatically set those fields, leave them empty or set them to
``@CLICK_ARCH@`` and ``@CLICK_FRAMEWORK@`` respectively.

Note: The app templates provided by Clickable make use of CMake's ``configure()`` to set
the fields in the ``manifest.json``.

Advanced Usage
--------------

.. _lxd:

Running Clickable in an LXD container
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

It is possible to run ``clickable`` in a container itself, using ``lxd``. This is not using ``--container-mode``, but allowing ``clickable`` to create docker containers as normal, but inside the existing ``lxd`` container. This may fail with a permissions error when mounting ``/proc``:

.. code-block:: bash

   docker: Error response from daemon: OCI runtime create failed: container_linux.go:349: starting container process caused "process_linux.go:449: container init caused \"rootfs_linux.go:58: mounting \\\"proc\\\" to rootfs \\\"/var/lib/docker/vfs/dir/bffeb203fe06662876a521b1bea3b74e4d5c6ea3535352215c199c75836aa925\\\" at \\\"/proc\\\" caused \\\"permission denied\\\"\"": unknown.

If this error occurs then ``lxd`` needs to be `configured to allow nested containers <https://stackoverflow.com/questions/46645910/docker-rootfs-linux-go-permission-denied-when-mounting-proc>` on the host:

.. code-block:: bash

   lxc stop your-container-name
   lxc config set your-container-name security.nesting true
   lxc start your-container-name
