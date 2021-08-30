#!/bin/bash

docker run \
    -v `pwd`:`pwd` \
    -w `pwd` \
    -v /tmp:/tmp \
    -e HOME=/tmp \
    -e CLICKABLE_SKIP_DOCKER_CHECKS=1 \
    -v /var/run/docker.sock:/var/run/docker.sock \
    clickable/clickable-ci \
    bash -c "pytest --cov=clickable ./tests"
