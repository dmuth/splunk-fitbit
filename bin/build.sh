#!/bin/bash
#
# Build our Splunk Fitbit container
#

# Errors are fatal
set -e

#
# Change to the parent of this script
#
pushd $(dirname $0) > /dev/null
cd ..

echo "# "
echo "# Building Docker container..."
echo "# "
docker build . -f Dockerfile-python -t splunk-fitbit-python
docker build . -f Dockerfile-splunk -t splunk-fitbit

echo "# "
echo "# Tagging container..."
echo "# "
docker tag splunk-fitbit-python dmuth1/splunk-fitbit-python
docker tag splunk-fitbit dmuth1/splunk-fitbit

echo "# Done!"

