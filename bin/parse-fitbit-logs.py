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
import statistics
import sys

log_dir = "/logs/"

logging.basicConfig(level = logging.INFO, format='%(asctime)s.%(msecs)03d: %(levelname)s: %(message)s',
	datefmt = '%Y-%m-%d %H:%M:%S'
	)

parser = argparse.ArgumentParser(description = 
	"Parse Fitbit logs and write them out in files for Splunk")
parser.add_argument('--num-days-sleep', type = int, default = 90,
                    help = "How many days of sleep data to process (default: 90)")
parser.add_argument('--num-days-heartrate', type = int, default = 30,
                    help = "How many days of heartrate data to process (default: 30)")
parser.add_argument('--rollup-interval', type = int, default = 300,
                    help = "How many seconds to do rollups into for heartrate data. (default: 300)")
parser.add_argument("--force", action = "store_true", 
	help = "Force overwriting non-zero byte files even if they exist!")

try:
	args = parser.parse_args()
except SystemExit:
	sys.exit(1)

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
def loopSleepLogs(dir, num_days, force):

	output_file = log_dir + "sleep.json"

	if os.path.exists(output_file):
		if os.stat(output_file).st_size == 0:
			logging.info("File {} exists, but is zero bytes, continuing...".format(output_file))
		else:
			if not force:
				logging.info("File {} exists, not overwriting it!".format(output_file))
				return()
			else:
				logging.info("--force specified, overwriting {}".format(output_file))
			
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
def heartrateRowToData(row, rollup_interval):

	retval = {}

	date_time_obj = datetime.datetime.strptime(row["dateTime"], "%m/%d/%y %H:%M:%S")
	date = date_time_obj.strftime("%Y-%m-%dT%H:%M:%S.000")

	timestamp = datetime.datetime.timestamp(date_time_obj)
	retval["period"] = timestamp // rollup_interval

	retval["dateTime"] = date
	retval["bpm"] = row["value"]["bpm"]
	retval["confidence"] = row["value"]["confidence"]

	return(retval)



#
# Loop through our rows, do rollup, and write them to the output file
#
def writeHeartRateLogs(output, rows, rollup_interval):

	count = 0
	current_period = ""
	current_date = ""
	bpms = []

	for row in rows:

		data = heartrateRowToData(row, rollup_interval)

		if data["period"] != current_period:

			if len(bpms):
				data2 = {}
				data2["dateTime"] = current_date
				data2["avg"] = statistics.mean(bpms)
				data2["median"] = statistics.median(bpms)
				data2["max_bpm"] = max(bpms)
				data2["min_bpm"] = min(bpms)
				data2["num_bpms"] = len(bpms)
				output.write(json.dumps(data2) + "\n")
				count += 1

			bpms = []
			current_period = data["period"]
			current_date = data["dateTime"]

		bpms.append(data["bpm"])

	#
	# If there is a final item, write one out.
	#
	if len(bpms):
		data2 = {}
		data2["dateTime"] = current_date
		data2["avg"] = statistics.mean(bpms)
		data2["median"] = statistics.median(bpms)
		data2["max_bpm"] = max(bpms)
		data2["min_bpm"] = min(bpms)
		data2["num_bpms"] = len(bpms)
		output.write(json.dumps(data2) + "\n")
		count += 1

	logging.info("{} rolled up events written".format(count))


#
# Loop through our directory for heartrate logs
#
def loopHeartrateLogs(dir, num_days, force, rollup_interval):

	output_file = log_dir + "heartrate.json"

	if os.path.exists(output_file):
		if os.stat(output_file).st_size == 0:
			logging.info("File {} exists, but is zero bytes, continuing...".format(output_file))
		else:
			if not force:
				logging.info("File {} exists, not overwriting it!".format(output_file))
				return()
			else:
				logging.info("--force specified, overwriting {}".format(output_file))
			
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

		logging.info("Writing {} rows to {} with a rollup interval of {}...".format(
			len(rows), output_file, rollup_interval))

		writeHeartRateLogs(output, rows, rollup_interval)

	output.close()



#
# Our main entry point.
#
def main(args):

	directory = "/mnt/fitbit/"
	if not os.path.exists(directory):
		raise Exception("Path {} does not exist!".format(directory))

	loopSleepLogs(directory, args.num_days_sleep, args.force)
	loopHeartrateLogs(directory, args.num_days_heartrate, args.force, args.rollup_interval)
	
main(args)


