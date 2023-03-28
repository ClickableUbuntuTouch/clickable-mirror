.. _env-vars:

Environment Variables
=====================

Environment variables will override values in the project config and can be
overridden by command line arguments.

In contrast to the environment variables described here that configure
Clickable, there are :ref:`environment variables <project-config-placeholders>` set by
Clickable to be used during build.

``CLICKABLE_ARCH``
------------------

Restricts build commands (``build``, ``build-libs``, ``desktop``) to the specified architecture. Architecture agnostic builds (``all``) are not affected. Useful in container mode.

``CLICKABLE_QT_VERSION``
------------------------

Overrides the project config's :ref:`qt_version <project-config-qt_version>`.

``CLICKABLE_FRAMEWORK``
-----------------------

Overrides the project config's :ref:`framework <project-config-framework>`.

``CLICKABLE_BUILDER``
---------------------

Overrides the project config's :ref:`builder <project-config-builder>`.

``CLICKABLE_BUILD_DIR``
-----------------------

Overrides the project config's :ref:`dir <project-config-build_dir>`.

``CLICKABLE_DEFAULT``
---------------------

Overrides the project config's :ref:`default <project-config-default>`.

``CLICKABLE_MAKE_JOBS``
-----------------------

Overrides the project config's :ref:`make_jobs <project-config-make-jobs>`.

``GOPATH``
----------

Overrides the project config's :ref:`gopath <project-config-gopath>`.

``CARGO_HOME``
--------------

Overrides the project config's :ref:`cargo_home <project-config-cargo_home>`.

``CLICKABLE_DOCKER_IMAGE``
--------------------------

Overrides the project config's :ref:`docker_image <project-config-docker-image>`.

``CLICKABLE_SKIP_DOCKER_CHECKS``
--------------------------------

Disables check whether docker is installed and properly set up.

``CLICKABLE_DOCKER_COMMAND``
----------------------------

Replaces the docker command. This is useful on systems where both, docker and
podman, are installed and Clickable would give podman precedence.

``CLICKABLE_BUILD_ARGS``
------------------------

Overrides the project config's :ref:`build_args <project-config-build-args>`.

``CLICKABLE_MAKE_ARGS``
------------------------

Overrides the project config's :ref:`make_args <project-config-make-args>`.

``OPENSTORE_API_KEY``
---------------------

Your api key for :ref:`publishing to the OpenStore <publishing>`.

``CLICKABLE_CONTAINER_MODE``
----------------------------

Same as :ref:`--container-mode <container-mode>`.

``CLICKABLE_SERIAL_NUMBER``
---------------------------

Same as :ref:`--serial-number <multiple-devices>`.

``CLICKABLE_SSH``
-----------------

Same as :ref:`--ssh <ssh>`.

``CLICKABLE_OUTPUT``
--------------------

Override the output directory for the resulting click file

``CLICKABLE_NVIDIA``
--------------------

Same as :ref:`--nvidia <nvidia>`.

``CLICKABLE_NO_NVIDIA``
-----------------------

Same as :ref:`--no-nvidia <nvidia>`.

``CLICKABLE_ALWAYS_CLEAN``
--------------------------

Overrides the project config's :ref:`always_clean <project-config-always-clean>`.

``CLICKABLE_NON_INTERACTIVE``
-----------------------------

Same as ``--non-interactive``

``CLICKABLE_DEBUG_BUILD``
-------------------------

Same as ``--debug``

``CLICKABLE_TEST``
------------------

Overrides the project config's :ref:`test <project-config-test>`.

``CLICKABLE_DARK_MODE``
-----------------------

Same as ``--dark-mode``

``CLICKABLE_ENV_<CUSTOM>``
--------------------------

Adds custom env vars to the build container. E.g. set
``CLICKABLE_ENV_BUILD_TESTS=ON`` to have ``BUILD_TESTS=ON`` set in the build
container.

Overrides env vars in :ref:`test <project-config-env_vars>`.

``CLICKABLE_DOCKER_REGISTRY``
-----------------------------

The Docker registry used to pull images. Defaults to ``docker.io`` to pull
from `Docker Hub <https://hub.docker.com/u/clickable>`__.
To use the `GitLab container registry <https://gitlab.com/groups/clickable/-/container_registries>`__
change this to ``registry.gitlab.com/clickable``.
