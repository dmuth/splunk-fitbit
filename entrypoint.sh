#!/bin/bash
#
# Entrypoint script--determine what it is we want to do.
#

if test "$1" == "--devel"
then
	echo "# "
	echo "# Starting container in devel mode and spawning a bash shell..."
	echo "# "
	exec "/bin/bash"

else
	exec /app/parse-fitbit-logs.py $@

fi

