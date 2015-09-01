#!/usr/bin/env python

''' Arguments are as folows:
    1 - Time length (w, m, 6m, y)
    2 - Data points to use (any integer)
    3 - Don't tweet graph straight away'''

'''Need to fix monthly graphs. Didn't run
    last time. Also 'yesterday' doesn't
    work if Monday falls on 2nd or 3rd of
    month!!!'''

import json
import time
import datetime
import os
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
import numpy as np
import matplotlib.dates as mdates
from pylab import *
from twython import Twython
import ConfigParser

# Variables
yesterday = datetime.date.today() - datetime.timedelta(days=1)
yesterday =  yesterday.strftime("%d-%b-%Y")
path = '/home/darreno/bgp_graphs/'
time_period = sys.argv[1]
points = int(sys.argv[2])
try:
    if sys.argv[3] == 'silent':
        silent = 1
except:
    silent = 0
if time_period == 'w':
        filename = path + 'bgp_weekly.json'
elif time_period == 'm':
        filename = path + 'bgp_monthly.json'
elif time_period == 'y' or time_period == '6m':
        filename = path + 'bgp_yearly.json'

# Read data
def loadvalues(filename):
    with open(filename, 'r') as f:
        entries = json.load(f)
    return entries

# Create Graphs
def graphdata(entries, family, time_period=time_period, points=points):
    date_time = []
    data_points = points
    use_points = 0
    if time_period == 'w':
        suffix = "-weekly.png"
        update = "week"
    elif time_period == 'm':
        suffix = "-monthly.png"
        update = "month"
    elif time_period == '6m':
        suffix = "-6monthly.png"
        update = "6 months"
    elif time_period == 'y':
        suffix = "-yearly.png"
        update = "year"

    if family == 4:
        prefixes = []
        data_type = 'v4total'
        title = 'IPv4'
        filename = path + 'graph_v4-' + yesterday + suffix
        colour = '#238341'
    elif family == 6:
        prefixes = []
        data_type = 'v6total'
        title = 'IPv6'
        filename = path + 'graph_v6-' + yesterday + suffix
        colour = '#0041A0'

    for entry in entries:
        use_points += 1
        if use_points == data_points:
            prefixes.append(entry[data_type])
            date_time.append(datetime.datetime.fromtimestamp(entry["time"]))
            use_points = 0

    plt.figure(figsize=(12,10))
    ax = subplot(111)
    xfmt = mdates.DateFormatter('%Y-%m-%d')
    ax.xaxis.set_major_formatter(xfmt)
    plt.suptitle(title + ' table movement for ' + update + ' ending ' + yesterday, fontsize=17)
    ax.grid(True)
    ax.spines["top"].set_visible(False)
    ax.spines["bottom"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.get_xaxis().tick_bottom()
    ax.get_yaxis().tick_left()
    plt.xticks(fontsize=12, rotation=12)
    plt.yticks(fontsize=12)
    plt.ticklabel_format(axis='y', style='plain', useOffset=False)
    plt.tick_params(axis="both", which="both", bottom="off", top="off",
                            labelbottom="on", left="off", right="off", labelleft="on")
    plt.plot(date_time, prefixes, 'o-', lw=1, alpha=0.4, color=colour)
    plt.figtext(0.5, 0.93, "data by: @mellowdrifter | www.mellowd.co.uk/ccie", fontsize=14, color='gray', ha='center', va='top', alpha=0.8)
    plt.savefig(filename)

def tweet(family, time_period=time_period):
    Config = ConfigParser.ConfigParser()
    Config.read('config')
    if time_period == 'w':
        status = 'Weekly BGP table movement: '
        suffix = "-weekly.png"
    elif time_period == 'm':
        status = 'Monthly BGP table movement: '
        suffix = "-monthly.png"
    elif time_period == '6m':
        status = '6 Month BGP table movement: '
        suffix = '-6monthly.png'
    elif time_period == 'y':
        status = 'Yearly BGP table movement: '
        suffix = "-yearly.png"
    if family == 4:
        consumer_key = Config.get('bgp4_account', 'consumer_key')
        consumer_secret = Config.get('bgp4_account', 'consumer_secret')
        access_token = Config.get('bgp4_account', 'access_token')
        access_token_secret = Config.get('bgp4_account', 'access_token_secret')
        filename = path + 'graph_v4-' + yesterday + suffix
    elif family == 6:
        consumer_key = Config.get('bgp6_account', 'consumer_key')
        consumer_secret = Config.get('bgp6_account', 'consumer_secret')
        access_token = Config.get('bgp6_account', 'access_token')
        access_token_secret = Config.get('bgp6_account', 'access_token_secret')
        filename = path + 'graph_v6-' + yesterday + suffix

    twitter = Twython(consumer_key, consumer_secret,
                      access_token, access_token_secret)

    with open(filename, 'rb') as image:
        response = twitter.upload_media(media=image)
        twitter.update_status(status=status, media_ids=[response['media_id']])


def main():
    entries = []
    if os.path.isfile(filename):
        entries = loadvalues(filename)

    graphdata(entries, 4)
    graphdata(entries, 6)
    if not silent:
        tweet(4)
        tweet(6)

if __name__ == "__main__":
    main()
