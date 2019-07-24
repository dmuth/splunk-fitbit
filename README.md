
# Splunking Fitbit Data

Some years ago, I bought a Fitbit Charge 2 so I could track my activity.
As a surprise to exactly no one, I have pretty bad sleeping habits.
Fitbit's dashboard is alright, but I wanted a little more freedom to do
data analytics on the data my way, and that's how this app came into being!

With Splunk Fitbit, the following metrics will be reported on:

- Sleep data
   - Nightly hours asleep, broken down by day of week
   - "Good" sleep days ( > 7 hours of sleep) and "Bad" sleep days ( < 7 hours) by week.
   - Trending good/bad sleep days over the last 30 days
- Heartrate data
   - Resting heartrate by day (more on how it's calculated below)
   - Trending minimum resting heartrate over the last 30 days
   - Trending maximum resting heartrate over the last 30 days
 
   
This app uses <a href="https://github.com/dmuth/splunk-lab">Splunk Lab</a>, an open-source 
app I built to effortlessly run Splunk in a Docker container.


# Screenshots



## Requirements

- Make sure Docker is installed



## Running The App

- Go to https://www.fitbit.com/settings/data/export and download your fitbit data
- Unzip the ZIP file
- Move your exported data into a local directory called `fitbit/`:
   - `mv path/to/fitbit/USERNAME/user-site-export fitbit`
- `SPLUNK_START_ARGS=--accept-license bash <(curl -s https://raw.githubusercontent.com/dmuth/splunk-fitbit/master/go.sh)`
   - This will run a Python script which will read in the JSON data from Fitbit (both types of data are in different formats...) and write it out into a `logs/` directory
   - If you want to change how many days back the script goes for either sleep or heartrate data, or change rollup values for heartrate data, add `-h` onto the end of that command to get syntax.
   - Then, Splunk will be started. Ingested data will be written to `splunk-data/`
- Go to <a href="https://localhost:8000/">https://localhost:8000/</a>, log in with the password you set, and you'll see your Fitbit data in a dashboard!


## Development

Mostly for my benefit, these are the scripts that I use to make my life easier:

- `./bin/build.sh` - Build the Python and Splunk Docker containers
- `./bin/push.sh` - Upload the Docker containers to Docker Hub
- `./bin/devel.sh` - Build and run the Splunk Docker container with an interactive shell
- `./bin/stop.sh` - Stop the Splunk container
- `./bin/clean.sh` - Stop Splunk, and remove the data and logs


## Notes/Bugs

- Don't bother trying to get steps--the data in the export doesn't match what's in the dashboard at ALL.  Step counts are wrong, days are missing, etc.  If Fitbit fixes this, then I will add in support. :-)
- I can't seem to get rangemaps working for nightly sleep hours, which is frustrating
- Heartrate data has an insane volume--nearly as often as 1 reading every 5 seconds.  So my import script will do rollup and output the avg/min/max/mean of all values.  By default, the rollup period is 5 minutes.  This can be adjusted, but may break certain assumptions in the graphs.
- I was able to approximate, but not perfectly match Fitbit's resting heartrate as reported on my personal dashboard on the site.  I ended up grabbing the 6 periods with the lowest minimum heartrate each day, and average those readings out to get a daily value.  Not great, not terrible.
   - I suspect that Fitbit's readings come from having higher granularity of the data, using only readings from the deepest part of sleep, and possibly throwing in a weighted average as well.


## Credits

I'd like to thank <a href="http://splunk.com/">Splunk</a>, for having such a kick-ass data
analytics platform, and the operational excellence which it embodies.

Also:
- <a href="http://patorjk.com/software/taag/#p=display&h=0&v=0&f=Standard&t=Splunk%20Lab">This text to ASCII art generator</a>, for the logo I used in the script.


## Copyright

Splunk is copyright by Splunk.  Apps included within Splunk Lab are copyright their creators,
and made available under the respective license.  


## Contact

- <a href="mailto:doug.muth@gmail.com">Email me</a>
- <a href="https://twitter.com/dmuth">Twitter</a>
- <a href="https://facebook.com/dmuth">Facebook</a>






