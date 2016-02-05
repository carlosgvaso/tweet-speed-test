#!/usr/bin/python2

# Tweets the ISP if the internet speed falls below s threshold.
####################################################################################

#import sys
import logging
import twitter
from csv import writer
from os.path import isfile
from subprocess import check_output, CalledProcessError
from datetime import datetime
from time import time

# Globals
####################################################################################
# Speed Test
speedtest_cmd = ["speedtest-cli", "--simple"]
test_result = None
ping = None
download = None
upload = None

down_speed_threshold = 4

date = datetime.fromtimestamp(time()).strftime('%Y-%m')

# CSV
csv_dir = "/home/alarm/speedtest/csv/"
csv_header = "Timestamp,Ping (ms),Download (Mbps),Upload (Mbps)\n"

# Twitter OAuth parameters
token = "940697372-29SzrOvWrKQ5jh9FxCgNbhEGv8LyUnGTYESMQiP1"
token_secret = "pO5vXmlaoDfpaFd1t3mv7CLzUQZbuh4Dq2CpnVW3fXYhF"
consumer_key = "8WkVLSsdi9gxjpWD7bdmzRk8O"
consumer_secret = "JbKava4nMCUSgEKhFBBrRJeYqbsCqKOUC6jcmPPdqHxmR2o7H0"

# Twitter statuses
tweet_down_msg = "Hey @ATT @Uverse @ATTCares why is my internet down? I pay for 6down\\1up in Austin, TX? #attoutage #att  #fixit"
tweet_slow_msg = "Hey @ATT @Uverse @ATTCares why is my internet speed {0:.2f}down\\{1:.2f}up when I pay for 6down\\1up in Austin, TX? #att #speedtest #fixit"

# Logger
log_level = logging.DEBUG
log_format = '%(asctime)s:%(levelname)s:%(funcName)s: %(message)s'
log_folder = "/home/alarm/speedtest/log/"
log_file = "speedtest-" + date + ".log" 

# Functions
####################################################################################
def speedTest():
	global test_result
	global ping
	global download
	global upload
	
        #run speedtest-cli
        logging.debug('Running speedtest')
	
	try:
        	output = check_output(speedtest_cmd)
	except CalledProcessError as e:
		logging.error('Code: %s: %s', e.returncode, e.output)
		return
        
	logging.debug('Finished speedtest')
        
	#split the 3 line result (ping,down,up)
        lines = output.split('\n')
	test_result = output
        logging.info('Test result: %s', output.replace('\n', ', ', 2).rstrip('\n'))
        
	#if speedtest could not connect set the speeds to 0
        if "Cannot" in output:
                ping = 100
                download = 0
                upload = 0
        #extract the values for ping down and up values
        else:
                ping = lines[0][6:11]
                download = lines[1][10:14]
                upload = lines[2][8:12]


def csvLog():
	# Get timestamp
        timestamp = datetime.fromtimestamp(time()).strftime('%Y-%m-%d %H:%M:%S')
        
	# Check if CSV file exists, else create a new one
	filename = csv_dir + "data-" + date + ".csv"
	if isfile(filename):
        	with open(filename, 'a') as out_file:
        		csv_w = writer(out_file)
        		csv_w.writerow((timestamp,ping,download,upload))
	else:
        	with open(filename, 'a') as out_file:
			out_file.write(csv_header)
        		csv_w = writer(out_file)
        		csv_w.writerow((timestamp,ping,download,upload))
	
	logging.info('CSV: %s, %s, %s, %s', timestamp, ping, download, upload)


def tweetResult():
        my_auth = twitter.OAuth(token, token_secret, consumer_key, consumer_secret)
        twit = twitter.Twitter(auth=my_auth)

        #try to tweet if speedtest couldnt even connet. Probably wont work if the internet is down
        if "Cannot" in test_result:
                try:
                        tweet = tweet_down_msg
                        twit.statuses.update(status = tweet)
                except Exception as e:
                        logging.error('%s', e)
                        return

        # tweet if down speed is less than whatever I set
        elif eval(download) < down_speed_threshold:
                print "trying to tweet"
                try:
                        tweet = tweet_slow_msg.format(eval(download), eval(upload))
                        twit.statuses.update(status=tweet)
                except Exception as e:
                        logging.error('%s', e)
			return
        return


# Main
####################################################################################
if __name__ == '__main__':
	logging.basicConfig(format = log_format, filename = log_folder + log_file, level = log_level)
        
	logging.info('Starting')
	
	speedTest()
	
	csvLog()
	
	tweetResult()
        
	logging.info('Stopping')


