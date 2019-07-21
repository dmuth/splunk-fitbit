#!/usr/bin/env python3
#
# Vim: :set tabstop=4
#
# Go through our Fitbit logs in a directory specified on the command line
# and write them out in /logs in a format that Splunk will understand.
#


import argparse
import datetime
import json
import logging
import os
import re
import sys

log_dir = "/logs/"

logging.basicConfig(level = logging.INFO, format='%(asctime)s.%(msecs)03d: %(levelname)s: %(message)s',
	datefmt = '%Y-%m-%d %H:%M:%S'
	)


parser = argparse.ArgumentParser(description = 
	"Parse Fitbit logs and write them out in files for Splunk")
parser.add_argument('--directory', metavar = 'DIRECTORY', type = str, required = True,
                    help = "Path to user-site-export/ direcotry in your Fitbit export")
parser.add_argument('--num-days', type = int, default = 30,
                    help = "How many days to go back in time (default: 30)")

args = parser.parse_args()
logging.info("Args: {}".format(args))


#
# Extract key pieces of data from a row of Fitbit's sleep data.
#
def sleepRowToData(row):

	retval = {}

	retval["dateOfSleep"] = row["dateOfSleep"] + "T00:00:00.000"
	retval["minutesAsleep"] = row["minutesAsleep"]
	retval["minutesAwake"] = row["minutesAwake"]
	retval["startTime"] = row["startTime"]
	retval["endTime"] = row["endTime"]
	retval["timeInBed"] = row["timeInBed"]
	retval["efficiency"] = row["efficiency"]

	return(retval)


#
# Loop through our directory for sleep logs
#
def loopSleepLogs(dir, num_days):

	output_file = log_dir + "sleep.json"
	logging.info("Opening output file {}...".format(output_file))
	output = open(output_file, "w")

	now = datetime.datetime.now()

	for filename in os.listdir(dir):

		if not filename.startswith("sleep-"):
			continue

		filename = dir + "/" + filename
		logging.info("Reading file {}...".format(filename))

		file = open(filename)
		rows = json.load(file)
		file.close()

		logging.info("Writing {} rows to {}...".format(len(rows), output_file))
		for row in rows:

			event_date = datetime.datetime.strptime(row["dateOfSleep"], "%Y-%m-%d")
			delta = (now - event_date).days
			if delta > num_days:
				logging.info("Skipping sleep on {} as it is older than {} days".format(event_date, num_days))
				continue

			data = sleepRowToData(row)
			output.write(json.dumps(data) + "\n")

	output.close()


#
# Extract key pieces of data from a row of Fitbit's heartrate data.
#
def heartrateRowToData(row):

	retval = {}

	date_time_obj = datetime.datetime.strptime(row["dateTime"], "%m/%d/%y %H:%M:%S")
	date = date_time_obj.strftime("%Y-%m-%dT%H:%M:%S.000")
	retval["dateTime"] = date
	retval["bpm"] = row["value"]["bpm"]
	retval["confidence"] = row["value"]["confidence"]

	return(retval)


#
# Loop through our directory for heartrate logs
#
def loopHeartrateLogs(dir, num_days):

	output_file = log_dir + "heartrate.json"
	logging.info("Opening output file {}...".format(output_file))
	output = open(output_file, "w")

	now = datetime.datetime.now()

	for filename in os.listdir(dir):

		if not filename.startswith("heart_rate-"):
			continue

		event_date = datetime.datetime.strptime(filename, "heart_rate-%Y-%m-%d.json")
		delta = (now - event_date).days
		if delta > num_days:
			logging.info("Skipping heartrate on {} as it is older than {} days".format(event_date, num_days))
			continue

		filename = dir + "/" + filename
		logging.info("Reading file {}...".format(filename))

		file = open(filename)
		rows = json.load(file)
		file.close()

		logging.info("Writing {} rows to {}...".format(len(rows), output_file))
		for row in rows:
			data = heartrateRowToData(row)
			output.write(json.dumps(data) + "\n")

	output.close()



#
# Our main entry point.
#
def main(args):

	if not os.path.exists(args.directory):
		raise Exception("Path {} does not exist!".format(args.directory))

	loopSleepLogs(args.directory, args.num_days)
	loopHeartrateLogs(args.directory, args.num_days)
	
main(args)


