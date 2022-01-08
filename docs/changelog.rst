.. _changelog:

Changelog
=========

Changes in v7.0.0
-----------------

For information on breaking changes and how to migrate from Clickable v6, check the :ref:`Migration Guide <migration>`.
There is also a migration tool referenced in the guide.

New features
^^^^^^^^^^^^

- Configure Clickable globally with a new :ref:`configuration file <config.yaml>`.
- Integrated bash completion, to set up run ``clickable setup completion``.
- Run Clickable from sub-directories, not only project root.
- Added new ``chain`` command to run multiple Clickable commands in a chain.
- Added new ``script`` command to run scripts defined in the clickable.json config file.
- Added new ``ci`` command to open a shell in the Clickable CI container.
- The ``run`` command can now be provided with a library name to run within the respective image.
- The ``create`` command allows to create apps non-interactively configuring the template with command line parameters.
- The ``gdb`` command allows to export a GDB init script that can be used by any IDE's remote debugger.
- The behavior of the ``gdb`` and ``gdbserver`` commands can be configured in detail via command line parameters.
- The ``test`` command now runs ``cargo test`` by default for the ``rust`` builder.
- The ``rust`` builder supports the ``rust_channel`` field to configure the desired tool chain (e.g. ``1.56.1`` or ``nightly``).
- The ``rust`` builder supports the ``build_args`` field in the project config (arguments are forwarded to cargo).
- The ``rust`` builder supports ``--verbose`` flag (forwarded to cargo).
- The ``rust`` builder supports Clickable libraries.
- The ``rust`` builder installs the binaries into ``lib/<ARCH_TRIPLET>/bin`` (does not apply to libraries).
- Project configuration now uses yaml format and project config is called ``clickable.yaml`` (``clickale.json`` is used as fallback and json format can still be used as it is a subset of yaml)
- Build commands can be either specified as a string or a list of strings (``prebuild``, ``build``, ``postmake``, ``postbuild``).
- Added ``install_root_data`` config field to list files for installation into the click package root directory.
- Improved ignored files field to match with wildcard characters.
- Added sanity checks for paths in the config.
- Added Desktop Mode env var to allow apps detecting Clickable Desktop Mode
- Library placeholders are available to successive libraries in the sequence (useful for linking libraries against other libraries).
- Library install directories are added to ``CMAKE_INSTALL_PREFIX`` for successive libraries in the sequence (to enable the usage of ``find_package()``).
- Set ``CMAKE_INSTALL_PREFIX`` in Qt Creator run configurations.
- ``dependencies_host``, ``dependencies_target`` and ``dependencies_ppa`` now support placeholders
- Added Godot template
- Support for running Clickable on arm64 MacOS devices (except for desktop mode)

Breaking Changes
^^^^^^^^^^^^^^^^

- Overhauled command line interface with proper sub-commands, each providing specific options. See ``clickable --help`` and ``clickable <sub-command> --help``.
- The default architecture changed from ``armhf`` to the host architecture. If you want the architecture of your test device as default, it can be configured in the :ref:`Clickable config <config.yaml>`.
- The default now is to do dirty builds, if you want to do a clean build use ``clickable build --clean`` or set ``always_clean`` config field or ``CLICKABLE_ALWAYS_CLEAN=ON`` env var.
- Merged the ``build-libs`` command into ``build``.
- Merged the ``clean-libs`` command into ``clean``.
- Merged the ``test-libs`` command into ``test``.
- Scripts can only be executed through the ``script`` command.
- The ``rust`` builder has been aligned to the other builders and does not try to install manifest and desktop file automatically anymore.
- The ``rust`` builder runs ``cargo install`` instead of ``cargo build``
- The ``go`` builder has been aligned to the other builders and does not try to install all files in the project dir automatically anymore.
- The ``go`` builder does not rename the produced binary anymore.
- The ``pure`` and ``cordova`` builders no longer override manifest ``architecture`` and ``framework`` fields, unless they are set to ``@CLICK_ARCH@`` and ``@CLICK_FRAMEWORK@``.
- ``prebuild`` and ``postbuild`` are executed within the build container.
- The image setup (``image_setup``, ``dependencies_*``, ``rust_channel``) is executed for custom docker images, too.
- The image setup can be skipped with the cli flag ``--skip-image-setup``.
- Removed deprecated configuration fields.

Bug Fixes
^^^^^^^^^

- The ``rust`` builder does not fail any more if the source dir (containing the Cargo.toml) is a sub-directory of the project dir.
- The ``rust`` builder does not try to update the tool chain on building any more (which would fail)
- The ``rust`` builder configures the cargo target directory to match the build dir, fixing cleaning via the ``clean`` command.
- The rustup cache is made writable in the container to fix permission issues on accessing it.
- The ``go`` builder configures the package dir to match the build dir, fixing cleaning via the ``clean`` command.
- Fixed app icons not displaying in Qt Creator.
- Fixed run configuration name in Qt Creator.
- Fixed crash for QtCreator when no exec args have been found
- Fixed ``shell`` command if public SSH key is ``id_ed25519.pub``.
- General polish and small bug fixes.
- Fix sound in desktop mode.

Changes in v6.24.2
------------------

- Fixed version checking when there is no internet connection

Changes in v6.24.1
------------------

- Fixed qmake building a pure qml app

Changes in v6.24.0
------------------

- Switched to use Qt 5.12 by default

Changes in v6.23.3
------------------

- When using the qmake builder a specific .pro file can be specified using the ``build_args`` setting
- Fixed cross-compiling for armhf with qmake when using Qt 5.12

Changes in v6.23.2
------------------

- Fixed version checker
- Fixed image update

Changes in v6.23.1
------------------

- Improved the Qt 5.9 docker images
- Rebuild docker images if the base image changes

Changes in v6.23.0
------------------

- Added new test-libs command to run tests on libs
- When using the verbosity flag make commands will also be verbose
- Fixed Qt version to Ubuntu framework mapping
- Added new version checker

Changes in v6.22.0
------------------

- Added more docs and improved error messages
- Added checks to avoid removing sources based on configuration
- Added support for building against Qt 5.12 or Qt 5.9
- Fixed rust problem when using nvidia

Changes in v6.21.0
------------------

- Added option to use an nvidia specific container for Clickable's ide feature
- Improved error messages when no device can be found
- Added option to set custom env vars for the build container via env vars provided to Clickable
- Improved how container version numbers are checked
- Improved checking for container updates
- Minor fixes

Changes in v6.20.1
------------------

- Fixed building libraries using make

Changes in v6.20.0
------------------

- Added support for armhf and arm64 hosts with new docker images
- Added support for env vars in image setup

Changes in v6.19.0
------------------

- Click review is now run after each build by default
- Added NUM_PROCS env var and placeholder for use in custom builders
- Enabled dependencies_ppa and image_setup in container mode
- Fixed issues detecting the timezone for desktop mode

Changes in v6.18.0
------------------

- Updated the ``clickable run`` command to use the container's root user

Changes in v6.17.1
------------------

- Fixed container mode when building libraries
- Added better handling of keyboard interrupts

Changes in v6.17.0
------------------

- Fixed errors when using ssh for some functions
- Added initial non-interactive mode to create new apps
- Added better error handling
- Allow opening qtcreator without a clickable.json file

Changes in v6.16.0
------------------

- Enhanced and fixed issues with the qtcreator support
- Fixed the docker_image setting

Changes in v6.15.0
------------------

- Vastly improved qtcreator support using ``clickable ide qtcreator``
- Improved docs
- Updated docs with the new Atom editor plugin
- Fixed the warning about spaces in the path
- Fixed various issues with container mode
- Fixed using gdb and desktop mode

Changes in v6.14.2
------------------

- Fixed issue where some directories were being created by root in the docker container
- Various documentation updates
- Restored the warning about spaces in the source path
- Fixed container mode so it doesn't check for docker images
- Fixed issues with env vars for libraries in container mode
- Added env vars to the ide command

Changes in v6.14.1
------------------

- Fixed issue when using the Atom editor extension
- Merged the C++ templates into one and included qrc compiling
- Minor bug fixes

Changes in v6.14.0
------------------

- Added new setup command to help during initial setup of Clickable
- Prevent building in home directory that isn't a click app

Changes in v6.13.1
------------------

- Fixed issue with an error showing the wrong message
- Fixed multiple ppas in ``dependencies_ppa``

Changes in v6.13.0
------------------

- Fixed packaging issues and published to pypi
- Fixed the builder auto detect showing up when it wasn't needed
- Added better errors when the current user is not part of the docker group
- Remove apps before installing them to avoid apparmor issues
- Various bug fixes
- Added optional git tag versioning in cmake based templates

Changes in v6.12.2
------------------

- Fixed bug checking docker image version
- Renamed build template to builder
- Fixed the publish command

Changes in v6.12.1
------------------

- Bug fixes
- Display nicer error messages when a template fails to be created
- Fixed auto detecting the build template

Changes in v6.12.0
------------------

- Added new feature for debugging via :ref:`valgrind <debugging-with-gdb>`
- Added new :ref:`ide <commands-ide>` command to allow running arbitrary graphical apps like qtcreator
- Code improvements
- Added versioning to the docker images to allow Clickable to depend on certain features in the image

Changes in v6.11.2
------------------

- Fixed the ``review`` and ``clean-build`` commands not working

Changes in v6.11.1
------------------

- Fixed the ``run`` command not working

Changes in v6.11.0
------------------

- Added :ref:`on device debugging with gdb <on-device-debugging>`.
- Deprecated chaining commands (this will be removed in the next major release)
- Fixed the build home directory for libraries
- Added error when trying to use docker images on unsupported host architectures
- Use the host architecture as the default when building in container mode
- Enable localhost access and pseudo-tty in run command
- When using CMake a Release build will be created unless ``--debug`` is specified
- Added new library placeholders
- Added new ``clean-build`` command
- Fixed issues with ``clickable create`` on older versions of Ubuntu
- Various minor bug fixes and code improvements

Changes in v6.10.1
------------------

- Fixed issues installing dependencies when in container mode

Changes in v6.10.0
------------------

- Fix containers being rebuilt when switching between desktop mode and building for amd64
- Enabled compiling rust apps into arm64
- Make ``install_data`` paths relative to the install dir
- Fixed the ``clickable create`` command when using an older version of git

Changes in v6.9.1
-----------------

- Fixed broken lib builds

Changes in v6.9.0
-----------------

- Placeholders are now allowed in env vars
- Changed placeholder syntax to ``${PLACEHOLDER}``, the old syntax is now deprecated
- Replaced ``dependencies_host`` with ``dependencies_build`` to avoid confusion about the name, ``dependencies_build`` is now deprecated
- Normalized env var names
- Added new ``precompiled`` build template to replace the now deprecated ``python`` build template
- Fixed issues using the ``install_*`` configuration options
- ``install_qml`` will now install qml modules to the correct nested path
- A per project home directory gets mounted during the build process
- Cleaned up arch handling and improved conflict detection

Changes in v6.8.2
-----------------

- Fixed broken architecture agnostic builds

Changes in v6.8.1
-----------------

- Fixed new architecture errors breaking architecture agnostic builds

Changes in v6.8.0
-----------------

- Fixed the ``ARCH`` placeholder breaking ``ARCH_TRIPLET`` placeholder
- Added new ``env_vars`` configuration for passing custom env vars to the build process
- Fixed errors on systems where /etc/timezone does not exist
- Added errors to detect conflicting architecture settings
- Improved multi arch support

Changes in v6.7.2
-----------------

- Fixed architecture mismatch error for architecture agnostic templates

Changes in v6.7.0
-----------------

- New error when there is no space left on the disk
- New error when the manifest's architecture does not match the build architecture
- New option to use ``@CLICK_ARCH@`` as the architecture in the manifest to allow Clickable to automatically set the architecture

Changes in v6.6.0
-----------------

- Fixed issue in with timezone detection
- Added better detection for nvidia mode and added a new --no-nvidia argument

Changes in v6.5.0
-----------------

- New bash completion, more info `here <https://gitlab.com/clickable/clickable/blob/master/BASH_COMPLETION.md>`__
- Fixed crash when running in container mode
- Added ``image_setup`` configuration to run arbitrary commands to setup the docker image
- Added arm64 support for qmake builds

Changes in v6.4.0
-----------------

- Use the system timezone when in desktop mode

Changes in v6.3.2
-----------------

- Fixed issues logging process errors
- Fixed issues parsing desktop files

Changes in v6.3.1
-----------------

- Updated `clickable create` to use a new template for a better experience
- Fixed desktop mode issue when the command already exits in the PATH
- Added a prompt for autodetecting the template type
- Improved Clickable's logging

Changes in v6.2.1
-----------------

- Fixed env vars in libs

Changes in v6.2.0
-----------------

- Replaced the ``--debug`` argument with ``--verbose``
- Switched the ``--debug-build`` argument to ``--debug``
- Initial support for running Clickable on MacOS
- Added new desktop mode argument ``--skip-build`` to run an app in desktop mode without recompiling

Changes in v6.1.0
-----------------

- Apps now use host locale in desktop mode
- Added ``--lang`` argument to override the language when running in desktop mode
- Added support for multimedia in desktop mode
- Make app data, config and cache persistent in desktop mode by mounting phablet home folder to ~/.clickable/home
- Added arm64 support and docker images (does not yet work for apps built with qmake)
- :ref:`Added placeholders and env vars to commands and scripts run via clickable <project-config-placeholders>`
- :ref:`Added option to install libs/qml/binaries from the docker image into the click package <project-config-install_lib>`
- Switched to a clickable specific Cargo home for Rust apps
- Click packages are now deleted from the device after installing
- Fixed ``dependencies_build`` not being allowed as a string
- Fixed issues finding the manifest file

Changes in v6.0.3
-----------------

- Fixed building go apps
- Fixed post build happening after the click is built

Changes in v6.0.2
-----------------

- Fixed container mode

Changes in v6.0.1
-----------------

- Added back click-build with a warning to not break existing apps

Changes in v6.0.0
-----------------

New features
^^^^^^^^^^^^

- When publishing an app for the first time a link to create it on the OpenStore will be shown
- Desktop mode can now use the dark theme with the ``--dark-mode`` argument
- Automatically detect when nvidia drivers are used for desktop mode
- Use native docker nvidia integration rather than nvidia-docker (when the installed docker version supports it)
- The UBUNTU_APP_LAUNCH_ARCH env var is now set for desktop mode
- Added remote gdb debugging in desktop mode via the ``--gdbserver <port>`` argument
- Added configurable ``install_dir``
- Libraries get installed when using ``cmake`` or ``qmake`` build template (into ``install_dir``)

Breaking Changes
^^^^^^^^^^^^^^^^

- The ``click-build`` command has been merged into the ``build`` command
- Removed deprecated configuration properties: ``dependencies``, ``specificDependencies``, and ``dir``
- Removed deprecated library configuration format
- Removed deprecated lxd support
- Moved the default build directory from ``build`` to ``build/<arch triplet>/app``
- Moved the default library build directory to ``build/<arch triplet>/<lib name>``
- Removed deprecated vivid support

Bug Fixes
^^^^^^^^^

- Fixed utf-8 codec error
- Use separate cached containers when building libraries
- Automatically rebuild the cached docker image for dependencies
