#!/bin/bash
#
# This script spins up Splunk to ingest Fitbit data.
#

# Errors are fatal
set -e

#
# Things the user can override
#
SPLUNK_PORT=${SPLUNK_PORT:-8000}
SPLUNK_PASSWORD=${SPLUNK_PASSWORD:-password1}
SPLUNK_DATA=${SPLUNK_DATA:-splunk-data}

DOCKER_IT=""
DOCKER_V=""

DEVEL_PYTHON=""
DEVEL_SPLUNK=""

if test ! "$SPLUNK_START_ARGS" -o "$SPLUNK_START_ARGS" != "--accept-license"
then
	echo "! "
	echo "! You need to access the Splunk License in order to continue."
	echo "! "
	echo "! Please restart this container with SPLUNK_START_ARGS set to \"--accept-license\""
	echo "! as follows:"
	echo "! "
	echo "! SPLUNK_START_ARGS=--accept-license"
	echo "! "
	exit 1
fi

PASSWORD_LEN=${#SPLUNK_PASSWORD}
if test $PASSWORD_LEN -lt 8
then
	echo "! "
	echo "! "
	echo "! Admin password needs to be at least 8 characters!"
	echo "! "
	echo "! Password specified: ${SPLUNK_PASSWORD}"
	echo "! "
	echo "! "
	exit 1
fi


ARG1=""

if test "$1" == "--devel-python"
then
	DOCKER_IT="-it"
	DOCKER_V="-v $(pwd)/bin:/app"
	DEVEL_PYTHON=1
	ARG1="--devel"

elif test "$1" == "--devel-splunk"
then
	DEVEL_SPLUNK=1
	ARG1="--devel"

fi

echo "# "
echo "# Parsing Fitbit logs..."
echo "# "
DOCKER_V_MNT="-v $(pwd):/mnt"
DOCKER_V_LOGS="-v $(pwd)/logs:/logs"
if test ! "$DEVEL_SPLUNK"
then
	docker run ${DOCKER_IT} ${DOCKER_V} ${DOCKER_V_LOGS} -v $(pwd):/mnt  dmuth1/splunk-fitbit-python $ARG1 $@
fi

if test "$DEVEL_PYTHON"
then
	exit 1
fi



#
# Create our Docker command line
#
DOCKER_NAME="--name splunk-fitbit"
DOCKER_RM="--rm"
DOCKER_V="-v $(pwd)/user-prefs.conf:/opt/splunk/etc/users/admin/user-prefs/local/user-prefs.conf"
DOCKER_PORT="-p ${SPLUNK_PORT}:8000"
DOCKER_LOGS="-v $(pwd)/logs:/logs"
DOCKER_DATA="-v $(pwd)/${SPLUNK_DATA}:/data"

#
# Create our user-prefs.conf which will be pulled into Splunk at runtime
# to set the default app.
#
cat > user-prefs.conf << EOF
#
# Created by Splunk Fitbit
#
[general]
default_namespace = splunk-fitbit
EOF

echo
echo "  ____            _                   _        _____   _   _     _       _   _   "
echo " / ___|   _ __   | |  _   _   _ __   | | __   |  ___| (_) | |_  | |__   (_) | |_ "
echo " \___ \  | '_ \  | | | | | | | '_ \  | |/ /   | |_    | | | __| | '_ \  | | | __|"
echo "  ___) | | |_) | | | | |_| | | | | | |   <    |  _|   | | | |_  | |_) | | | | |_ "
echo " |____/  | .__/  |_|  \__,_| |_| |_| |_|\_\   |_|     |_|  \__| |_.__/  |_|  \__|"
echo "         |_|                                                                     "
echo 


echo "# "
echo "# About to run Splunk Fitbit!"
echo "# "
echo "# Before we do, please confirm these settings:"
echo "# "
echo "# URL:                               https://localhost:${SPLUNK_PORT}/ (Set with \$SPLUNK_PORT)"
echo "# Login/Password:                    admin/${SPLUNK_PASSWORD} (Set with \$SPLUNK_PASSWORD)"
echo "# Splunk Data Directory:             ${SPLUNK_DATA} (Set with \$SPLUNK_DATA)"
echo "# "

if test "$SPLUNK_PASSWORD" == "password1"
then
	echo "# "
	echo "# PLEASE NOTE THAT YOU USED THE DEFAULT PASSWORD"
	echo "# "
	echo "# If you are testing this on localhost, you are probably fine."
	echo "# If you are not, then PLEASE use a different password for safety."
	echo "# If you have trouble coming up with a password, I have a utility "
	echo "# at https://diceware.dmuth.org/ which will help you pick a password "
	echo "# that can be remembered."
	echo "# "
fi


echo "> "
echo "> Press ENTER to run Splunk Fitbit with the above settings, or ctrl-C to abort..."
echo "> "
read


CMD="${DOCKER_RM} ${DOCKER_NAME} ${DOCKER_PORT} ${DOCKER_LOGS} ${DOCKER_DATA} ${DOCKER_V}"
CMD="${CMD} -e SPLUNK_START_ARGS=${SPLUNK_START_ARGS}"
CMD="${CMD} -e SPLUNK_PASSWORD=${SPLUNK_PASSWORD}"

if test ! "$DEVEL_SPLUNK"
then
	ID=$(docker run $CMD -d dmuth1/splunk-fitbit)

else
	DOCKER_V_APP="-v $(pwd)/app:/opt/splunk/etc/apps/splunk-fitbit/local"
	docker run $CMD ${DOCKER_V_MNT} ${DOCKER_V_APP} -it dmuth1/splunk-fitbit bash

fi

echo "# "
echo "# Splunk Fitbit launched with Docker ID: "
echo "# "
echo "# ${ID} "
echo "# "
echo "# To check the logs for Splunk Fitbit: docker logs splunk-fitbit"
echo "# "
echo "# To kill Splunk Fitbit: docker kill splunk-fitbit"
echo "# "


