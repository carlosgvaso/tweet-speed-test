#!/usr/bin/env python3

# Tweets the ISP if the internet speed falls below s threshold.
####################################################################################

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
speedtest_cmd = ['speedtest-cli', '--simple']
test_result = None
ping = None
download = None
upload = None

down_speed_threshold = 4

date = datetime.fromtimestamp(time()).strftime('%Y-%m')

# CSV
csv_dir = './'      # You can change this
csv_header = 'Timestamp,Ping (ms),Download (Mbps),Upload (Mbps)\n'

# Twitter OAuth parameters (add you own here)
token = ''
token_secret = ''
consumer_key = ''
consumer_secret = ''

# Twitter statuses
tweet_down_msg = 'Hey @ATT @Uverse @ATTCares why is my internet down? I pay for 6down\\1up in Austin, TX? #attoutage #att  #fixit'
tweet_slow_msg = 'Hey @ATT @Uverse @ATTCares why is my internet speed {0:.2f}down\\{1:.2f}up when I pay for 6down\\1up in Austin, TX? #att #speedtest #fixit'

# Logger
log_level = logging.DEBUG
log_format = '%(asctime)s:%(levelname)s:%(funcName)s: %(message)s'
log_folder = './'       # You can change this
log_file = 'speedtest-' + date + '.log' 

# Functions
####################################################################################
def speedTest():
    global test_result
    global ping
    global download
    global upload
    
    # Run speedtest-cli
    logging.debug('Running speedtest')
    
    try:
        output = str(object=check_output(speedtest_cmd), encoding='utf-8', errors='strict')
    except CalledProcessError as e:
        logging.error('Code: {0}: {1}'.format(e.returncode, e.output))
        return
    
    logging.debug('Finished speedtest')
    
    #split the 3 line result (ping,down,up)
    lines = output.splitlines()
    test_result = output
    logging.info('Test result: {0}, {1}, {2}'.format(lines[0], lines[1], lines[2]))
    
    #if speedtest could not connect set the speeds to 0
    if 'Cannot' in output:
        ping = 100
        download = 0
        upload = 0
    else:   #extract the values for ping down and up values
        ping = lines[0][6:11]
        download = lines[1][10:14]
        upload = lines[2][8:12]


def csvLog():
    # Get timestamp
    timestamp = datetime.fromtimestamp(time()).strftime('%Y-%m-%d %H:%M:%S')
    
    # Check if CSV file exists, else create a new one
    filename = csv_dir + 'data-' + date + '.csv'
    if isfile(filename):
        with open(filename, 'a') as out_file:
            csv_w = writer(out_file)
            csv_w.writerow((timestamp,ping,download,upload))
    else:
        with open(filename, 'a') as out_file:
            out_file.write(csv_header)
            csv_w = writer(out_file)
            csv_w.writerow((timestamp,ping,download,upload))
    
    logging.info('CSV: {0}, {1}, {2}, {3}'.format(timestamp, ping, download, upload))


def tweetResult():
    my_auth = twitter.OAuth(token, token_secret, consumer_key, consumer_secret)
    twit = twitter.Twitter(auth=my_auth)
    
    #try to tweet if speedtest couldnt even connet. Probably wont work if the internet is down
    if 'Cannot' in test_result:
        logging.debug('Trying to tweet')
        try:
            tweet = tweet_down_msg
            twit.statuses.update(status = tweet)
        except Exception as e:
            logging.error('{0}'.format(e))
            return
    
    # tweet if down speed is less than whatever I set
    elif eval(download) < down_speed_threshold:
        logging.debug('Trying to tweet')
        try:
            tweet = tweet_slow_msg.format(eval(download), eval(upload))
            twit.statuses.update(status=tweet)
        except Exception as e:
            logging.error('{0}'.format(e))
            return
    return


# Main
####################################################################################
if __name__ == '__main__':
    logging.basicConfig(format = log_format, filename = log_folder + log_file, level = log_level)
    
    logging.info('Starting {0}'.format(__name__))
    
    speedTest()
    
    csvLog()
    
    tweetResult()
    
    logging.info('Stopping {0}'.format(__name__))

