#!/bin/bash

# Errors are fatal
set -e


#
# Change to the parent of this script
#
pushd $(dirname $0) > /dev/null
cd ..

./bin/build.sh

./go.sh --devel-splunk


