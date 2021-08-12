#!/bin/bash

docker run -v `pwd`:`pwd` -w `pwd` clickable/testing bash -c "./clickable-dev --help"
