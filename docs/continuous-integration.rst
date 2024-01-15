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
`blog post <https://blog.bhdouglass.com/clickable/tutorial/2019/03/18/publishing-apps-to-the-0penstore-with-gitlab-ci.html>`__.
This method can also be adapted for other CI solutions.

A working template of a `.gitlab-ci.yml` for a pure qml app is given below. This config takes care of three things:
1. it builds the app when commits are pushed for three architectures amd64, arm64 and armhf
2. it releases the app to OpenStore when a tag is pushed with the last commit message as changelog
3. it creates a Gitlab release when a tag is pushed with the last commit message as release description

.. code-block:: bash

    stages:
        - build
        - publish
        - release

    .armhf: &armhf
        variables:
            ARCH: "armhf"
            ARCH_TRIPLET: "arm-linux-gnueabihf"

    .arm64: &arm64
        variables:
            ARCH: "arm64"
            ARCH_TRIPLET: "aarch64-linux-gnu"

    .amd64: &amd64
        variables:
            ARCH: "amd64"
            ARCH_TRIPLET: "x86_64-linux-gnu"

    .build:
        image: "clickable/ci-20.04-$ARCH"
        stage: build
        script: 'clickable build --clean --arch $ARCH'
        artifacts:
            paths:
                - "build/$ARCH_TRIPLET/app"
            expire_in: 1 week

    build-armhf:
        <<: *armhf
        extends: .build

    build-arm64:
        <<: *arm64
        extends: .build

    build-amd64:
        <<: *amd64
        extends: .build

    publish:
        stage: publish
        image: "clickable/ci-20.04-armhf"
        rules:
            - if: $CI_COMMIT_TAG
        script:
            - 'clickable publish "$CI_COMMIT_MESSAGE"'
            - 'clickable publish --arch arm64'
            - 'clickable publish --arch amd64'
        dependencies:
            - build-armhf
            - build-arm64
            - build-amd64
        artifacts:
            paths:
                - build/arm-linux-gnueabihf/app/*.click
                - build/aarch64-linux-gnu/app/*.click
                - build/x86_64-linux-gnu/app/*.click
            expire_in: 30 days

    release_job:
    stage: release
    image: registry.gitlab.com/gitlab-org/release-cli:latest
    rules:
        - if: $CI_COMMIT_TAG
    script:
        - echo "running release_job"
    release:
        tag_name: '$CI_COMMIT_TAG'
        description: "$CI_COMMIT_MESSAGE"