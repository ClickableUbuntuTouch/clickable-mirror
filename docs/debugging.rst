.. _debugging-with-gdb:

Debugging
=========

Clickable does not separate build caches for different build types. Therefore make
sure to create a clean debug build, e.g. via
``clickable build --debug --clean --arch arm64``.

Desktop Mode
------------

The easiest way to do GDB Debugging via Clickable is desktop mode and can be started
by running ``clickable desktop --gdb``.

Alternatively a GDB Server can be started with ``clickable desktop --gdbserver <port>``
(just choose any port, e.g. ``3333``). Check for an option to do GDB Remote Debugging
in your IDE and connect to ``localhost:<port>``. To connect a GDB Client run
``gdb <app-binary> -ex 'target remote localhost:<port>'``.

To analyze errors in memory access run ``clickable desktop --valgrind``.

.. _on-device-debugging:

On Device
---------

Two terminals are required to do debugging on the device, one to start the ``gdbserver``
and the other one to start ``gdb``. In the first terminal run ``clickable gdbserver``
and in the second one ``clickable gdb``. This method is limited to
apps that are started via their own binary file.

For Debugging in your IDE, run ``clickable gdb --script debug.gdbinit``. This creates
a GDB script that can be configured as init script in your IDE's GDB Remote Debugging
feature. To execute the script from a gdb shell (e.g. gdb-multiarch) run
``source debug.gdbinit``.

For detailed instructions on how to use gdb check out
`gdb documentation <https://sourceware.org/gdb/current/onlinedocs/gdb/>`__.
