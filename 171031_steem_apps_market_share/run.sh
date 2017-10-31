#!/bin/bash

CONTAINER="steem-app-analysis"

mkdir -p steemdata
docker build -t ${CONTAINER} .
docker run -v $PWD/steemdata:/steemdata ${CONTAINER}
