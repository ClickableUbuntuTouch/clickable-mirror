#!/bin/bash

RELEASE=${1:-focal}

docker run \
    -v `pwd`/../:`pwd`/../ \
    -w `pwd` \
    -u `id -u` \
    --rm \
    -it clickable/build-deb:$RELEASE \
    bash -c "dpkg-buildpackage && dh_clean"
