.. _continuous-integration:

Continuous Integration
======================

Clickable CI Docker Images
--------------------------

CI docker images are available for easily using Clickable with a continuous
integration setup. They can be found on Docker hub: ``clickable/ci-20.04-armhf``,
``clickable/ci-20.04-amd64`` and ``clickable/ci-20.04-arm64``.
The images come with Clickable pre installed and already setup in container mode.

GitLab CI Tutorial
------------------

For a full guide to setting up GitLab CI with a Clickable app check out this
`blog post <https://bhdouglass.com/blog/publishing-apps-to-the-openstore-with-gitlab-ci/>`__.
This method can also be adapted for other CI solutions.

A working template of a `.gitlab-ci.yml` for building and publishing your app can be found in the `clickable app template <https://gitlab.com/clickable/ut-app-meta-template/-/blob/master/{{cookiecutter['App Name']}}/.gitlab-ci.yml>`__. If you also wish to have an automatic gitlab release to be created when pushing a tag, follow `gitlabs docs <https://docs.gitlab.com/ee/ci/yaml/#release>`__. To use the last commit message as description use this configuration `description: "$CI_COMMIT_MESSAGE"`.