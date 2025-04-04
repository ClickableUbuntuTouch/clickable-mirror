.. _changelog:

Changelog
=========

Changes in v8.3.0
-----------------

- Added support for building Noble apps (``ubuntu-touch-24.04-1.x``)
- Made the timeout longer when detecting the attached device's architecture
- Fixed issues running the ``gdb`` command
- Added an option to specify an app hook when debugging with gdb
- Fixed the gdb server not getting killed when Clickable exits

Changes in v8.2.0
-----------------

- ``gdbserver`` will only be copied to the device if needed when running ``clickable gdbserver``
- Fixed the ``--serial-number`` throwing errors due to a typo
- Updated error messages when connecting to the OpenStore to include different messages when there are connection errors and connection timeouts
- Fixed Godot template apps running under Clickable Desktop

Changes in v8.1.0
-----------------

- Added support for rootless Docker Desktop
- Released Clickable snap package
- Fixed bug with paths starting with a placeholder
- Fixed ``no-lock`` command for focal
- Reverted unintended CMake downgrade in Clickable containers

Changes in v8.0.1
-----------------

- Changed default framework to 20.04.1
- Improved error message when the manifest is missing
- Added workaround for ADB access on Xenial devices (added ``--xenial-adb`` to enforce and speed it up)
- Fixed using gdbserver on Focal
- Fixed ``shell`` and ``setup`` commands warning about missing project
- Fix installing libraries by name instead of full path via ``install_lib``
- Fix reusing cached docker images

Changes in v8.0.0
-----------------

For information on breaking changes and how to migrate from Clickable v7, check the :ref:`Migration Guide <migration8>`.

New Features
^^^^^^^^^^^^

- Clickable will now :ref:`automatically detect device architecture <device-detection>` for you.
    - This can be overriden by the new ``default_arch`` configuration.
- A ``target`` can be specified (either ``adb``, ``ssh``, or ``host``). By default Clickable will auto detect the target (ssh or adb).
    - This can be overriden by the new ``default_target`` configuration.

Breaking Changes
^^^^^^^^^^^^^^^^

- Focal is now the default framework. All clicks will be built against 20.04 :ref:`unless otherwise specified <project-config-framework>`.
- Cordova support has been dropped as it is no longer maintained upstream.
- Node.js has been removed from the Clickable docker images since it is no longer needed for Cordova.

Bug Fixes
^^^^^^^^^

- Deduplicates directories for ``install_libs`` to reduce warnings.
- Fixed warning popup when using QtCreator.
- The ssh welcome message is now suppressed for cleaner log output.
- Fixed Godot games not having hardware acceleration on Focal.

Changes in v7.12.3
------------------

- Fixed crash when using arch "all" for libs

Changes in v7.12.2
------------------

- Added support for Lunar and Mantic to the Ubuntu PPA

Changes in v7.12.1
------------------

- Fixed CMake install prefix bug
- Marked the Cordova builder as deprecated. It will be removed in v8.

Changes in v7.12.0
------------------

- Added new command ``clean-images`` to remove obsolete Clickable Docker images
- Added environment variable to change the Docker registry used to pull images
- Docker images are now published on GitLab's container registry in addition to Docker Hub
- Changed automatically setting the CMake release type and prefix to not override any values set in the build args
- Improved Docker image lookup
- Improved timeout handling during the publish command
- Fixed QtCreator build
- Fixed the initial setup of CMake projects in QtCreator for Focal
- Fixed Go linker issue for Focal

Changes in v7.11.0
------------------

- Desktop mode commands (like ``test``) can now be used in container mode
- Disabled the image version check when a custom Docker image is being used
- Added ``--all`` flag to the ``clean`` command for cleaning all build dirs at once
- Fixed cleaning build dirs when using the ``build`` command with ``--clean --all``
- Reduced the number of Docker layers when Clickable generates an image

Changes in v7.10.0
------------------

- Clickable placeholders are now available in ``image_setup``
- ``desktop --gdb`` now implies ``--debug``
- Fixed debug symbol export

Changes in v7.9.0
-----------------

- Added support for dark mode when using Focal based desktop mode
- Fixed icons not showing correctly in desktop mode

Changes in v7.8.0
-----------------

- Added warning when trying to build an app without libraries being built first
- Dropped Qt 5.9 support
- Switched to using fully qualified docker image names to fix an issue with Podman
- Fixed bug cleaning desktop mode directories

Changes in v7.7.3
-----------------

- Fixed installing QML modules

Changes in v7.7.2
-----------------

- Fixed crash when using Python 3.11
- Fixed command outputs not being displayed

Changes in v7.7.1
-----------------

- Fixed installing files with podman

Changes in v7.7.0
-----------------

- Removed Atom support from the ``ide`` command as it has been [sunsetted](https://github.blog/2022-06-08-sunsetting-atom/)
- Fixed crash in desktop mode when the docker container doesn't exist

Changes in v7.6.0
-----------------

- Added new QBS builder
- Added live reloading for qmlscene based apps in desktop mode
- Added support to configure the SSH port
- Added a configurable timeout when publishing click packages
- Added more options for the clean command
- Added ``CLICKABLE_DOCKER_COMMAND`` env variable to choose between podman and docker
- ``clickable --version`` will always check for updates
- Fixed Clickable trying to setup docker when podman is being used
- Fixed running commands via adb on Focal devices
- Fixed checking for systemd on non-Linux systems
- Fixed getting logs from Focal devices
- Fixed desktop mode crashing when pulse directories are not found

Changes in v7.5.0
-----------------

- Added support for running Clickable with Podman
- Added support for running Clickable on Fedora
- Added support for cross compiling Focal clicks
- Added support for building Focal clicks on arm64 hosts
- Added support for Focal for the ``ide`` and ``ci`` commands
- Added support for Focal to the nvidia images
- Fixed timezone in desktop mode
- Added support for ``clickable.yml`` files in addition to ``clickable.yaml``
- Added support for installing and launching clicks on Focal devices
- Fixed some issues running Clickable on Windows Subsystem for Linux (support is not complete yet)

Changes in v7.4.0
-----------------

- Added initial support for building clicks for Focal (Currently only supporting amd64 builds)
- When using ``install_lib``, common library locations will be searched
- When using ``install_bin``, the PATH will be searched

Changes in v7.3.0
-----------------

- Fix NUM_PROCS placeholder for libs
- Updated docs for library commands
- Fix env var issues between apps and libs
- Updated container mode to use image_setup env vars
- Added configuration options to ignore review warnings and/or errors
- Moved warning about framework to a debug message
- ``@`` is now allowed in paths
- Fixed the skip_review option when chaining commands

Changes in v7.2.0
-----------------

- Removed deprecated go build flag
- Fixed the bash completion setup to only run the setup once
- Fixed commands run in Docker containers not being stopped with CTRL+C
- The ? wildcard can be used in install paths
- The build command now fail if the review also fails, use ``skip_review`` for unconfined apps

Changes in v7.1.2
-----------------

- Fixed the Rust cargo settings for building armhf packages

Changes in v7.1.1
-----------------

- Updated framework list
- Fixed issue when setting up docker group
- The current user is no longer automatically added to docker group
- ``clickable setup`` now includes warning about security implications adding the current user to the docker group
- Fixed double cleaning when using the ``always_clean`` option
- Fixed migration warning showing at the wrong times
- Fixed ``clickable_minimum_required`` to also allow numbers
- Fixed prebuild and postbuild for libraries
- Added more logging for docker commands

Changes in v7.1.0
-----------------

- ``restrict_arch`` can now be used with libraries
- Fixed ``make_args`` not working as expected when specified as a list
- Removed desktop file places holder when executing an app in desktop mode
- Fixed ``clickable ide qtcreator`` not working

Changes in v7.0.1
-----------------

- Fixed dependency issues

Changes in v7.0.0
-----------------

For information on breaking changes and how to migrate from Clickable v6, check the :ref:`Migration Guide <migration7>`.
There is also a migration tool referenced in the guide.

New features
^^^^^^^^^^^^

- Configure Clickable globally with a new :ref:`configuration file <config>`.
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
- The default architecture changed from ``armhf`` to the host architecture. If you want the architecture of your test device as default, it can be configured in the :ref:`Clickable config <config>`.
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
