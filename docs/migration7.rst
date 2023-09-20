.. _migration7:

Clickable 7 Migration
=====================

This guide describes the changes that come with Clickable 7 and how to migrate a
project from Clickable 6. The suggestions described here can be applied
automatically using the
`clickable-migration <https://crates.io/crates/clickable-migration>`__ tool.

Clean Building
--------------

Clickable 6 was cleaning the build directory before each build by default.
If you want to keep that behaviour for your project, add to your
project config:

.. code-block:: javascript

    "always_clean": true

This behaviour can also be enabled temporarily by setting the environment variable
``CLICKABLE_ALWAYS_CLEAN=ON`` or passing ``--clean`` to a build command. Example:
``clickable build --clean``

This means the ``clean-build`` command has been removed, as it is not needed
anymore. This also means that the keyword ``dirty`` and the environment variable
``CLICKABLE_DIRTY`` are no longer needed nor supported.

Unconfined Apps
---------------

The build command fails if there are review warnings or errors, because the Open
Store refuses the upload of click packages in that case. Unconfined apps need to
configure review warnings to be ignored:

.. code-block:: javascript

    "ignore_review_warnings": true

Command Line Interface
----------------------

The command line interface has seen a complete overhaul, eliminating the
glitches we saw with the old one and enabling a lot of improvements. To get
an overview run ``clickable --help``.

Bash Completion
^^^^^^^^^^^^^^^

Clickable 7 supports bash completion through ``argcomplete``. Run the setup and
confirm to enable bash completion ``clickable setup completion``.

If you use another shell, check `argcomplete docs <https://kislyuk.github.io/argcomplete/>`__
on whether it is supported and how to enable it.

Commands
^^^^^^^^

Clickable 7 introduces proper commands providing specific parameters and help
messages. Example: ``clickable create --help``.

Chaining Commands
^^^^^^^^^^^^^^^^^

In Clickable 6 you could chain commands like ``clickable build install launch logs``.
On one hand this was practical, on the other it caused a lot of issues with
different commands. This is not possible anymore with Clickable 7. But don't be afraid!
The ``chain`` command got your back.
Example: ``clickable chain build install launch logs``

If no command is provided to ``chain`` it will run the default chain
``build install launch``, which can even be configured through the ``default`` field.
And finally a pure ``clickable`` is equivalent to ``clickable chain``. So not much
changed after all.

Libraries
^^^^^^^^^

Libraries are now cleaned and built by the same commands as the app itself. Run
``clickable build --libs`` to build libraries, ``clickable clean --libs`` to clean them 
and ``clickable test --libs`` for running unit tests.

Update
^^^^^^

The ``update`` command has been renamed to ``update-images`` because it was often
misunderstood as a command to update clickable. In fact, it does only update the
clickable docker images.

Project Configuration File
--------------------------

The ``clickable.json`` has a successor: ``clickable.yaml``. The schema did not change,
just the format. YAML allows to write better human-readable and cleaner config files.

If you just want to keep your config file as is, you can do so, because YAML is a
superset of JSON. It is recommended to rename the file to ``clickable.yaml``. But even
if you keep the file name ``clickable.json``, Clickable will find it after looking for a
``clickable.yaml``.

Builders
--------

Rust
^^^^

In Clickable 6 the Rust builder would install files such as the manifest or assets.
In order to be more flexible and better aligned with the other builds, this behaviour
was removed from the builder and added as ``install_root_data`` field in the Rust app
template. For existing Rust apps adding that field might be necessary as well.

The Rust builder now configures the target directory to the build directory configured
with Clickable in order to make the ``clean`` command work correctly for Rust apps.

The Rust builder now runs ``cargo install`` instead of ``cargo build``. It also
supports ``build_args`` in your project config now.

The Rust builder can now be used in libraries, too. The Rust builder explicitly
specifies the rust channel to avoid unintended rustup calls that would fail due to
missing permissions in the container.

The channel can now be configured via the field ``rust_channel`` which makes it easy
to use ``nightly`` or pin the rust version as desired (e.g. ``1.56.1``).

Go
^^

In Clickable 6 the Go builder would install files all files from the project folder
unless they were listed in ``ignore``.
In order to be more flexible and better aligned with the other builds, this behaviour
was removed from the builder. Installing necessary files and folders has been added as
``install_root_data`` field in the Go app template. For existing Go apps adding that
field might be necessary as well.

The Go builder now configures the package directory to the build directory configured
with Clickable in order to make the ``clean`` command work correctly for Go apps.

The Go builder no longer renames the produced binary based on the manifest.

Pure and Cordova
^^^^^^^^^^^^^^^^

In Clickable 6 pure and cordova builders would silently override ``architecture`` and
``framework`` fields in the app manifest. This behaviour was removed. For existing apps
relying on the old behaviour one might need to set those fields correctly or let
Clickable override it by setting the fields to ``@CLICK_ARCH@`` or ``@CLICK_FRAMEWORK@``
accordingly.

Some time in the past, the pure builder app template contained a CMake configuration
that would configure the manifest ``architecture`` field to ``amd64`` when it actually
should be ``all``. If that is the case for your app, just remove the command that
sets the variable ``CLICK_ARCH``.

Custom Build Commands
---------------------

In contrast to previous versions, Clickable 7 executes ``prebuild`` and ``postbuild``
commands within the build container, making it independent of tools installed on host
side.

Clickable 7 lets you specify a list of commands for ``prebuild``, ``build``,
``postmake`` and ``postbuild`` besides the possibility of specifying a single string.

Container Handling
------------------

Unlike previous versions, Clickable 7 does not skip the image setup for custom docker images. If
skipping is still desired, the command line flag ``--skip-image-setup`` can be used.

Removal of Deprecated Things
----------------------------

Clickable 6 still accepted some deprecated keywords, which are rejected by
Clickable 7.

Architecture
^^^^^^^^^^^^

Instead of setting ``arch`` in your project config you should specify the
architecture you want to build for via command line.
Example: ``clickable build --arch arm64``

In case your app is restricted to one specific architecture for some reason, you
can still set ``restrict_arch``. Example:

.. code-block:: javascript

    "restrict_arch": "arm64"

If the environment used with container mode only supports compiling for one
specific architecture, you should set the environment variable ``CLICKABLE_ARCH``.

Build Templates
^^^^^^^^^^^^^^^

Clickable 6.12.2 changed the naming of build templates to builders in order to
avoid confusion with app templates. A builder is rather a recipe for building than
a template anyways. Clickable 7 now rejects the keyword ``template``. You can use
``builder`` as a drop-in replacement.

Python Builder
^^^^^^^^^^^^^^

Use the ``precompiled`` builder if your Python-based app contains architecture
specific files or the ``pure`` template otherwise.

Dependencies
^^^^^^^^^^^^

Clickable can install build dependencies via ``apt``. Some of them are build tools
you need on your host during the build, such as ``ninja`` or ``libtool``. We call
these host dependencies. Others are libraries used by your app and need to be
installed for the target architecture. We call these target dependencies. Clickable
needs to distinguish them as they need to be installed for different architectures.

Clickable 6 still accepted host dependencies through the deprecated keyword
``dependencies_build``. Clickable 7 only accepts host dependencies through
``dependencies_host``. The keyword for target dependencies remains
``dependencies_target``.

Click Build Command
^^^^^^^^^^^^^^^^^^^

The click packaging is done by the ``build`` command. Clickable 6 still accepted the
deprecated ``click-build`` command, which would only print a deprecation message.
This ancient command has been removed completely in Clickable 7.

