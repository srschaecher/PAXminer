#!/usr/bin/env python3
'''
This script was written by Beaker from F3STL. Questions? @srschaecher on twitter or srschaecher@gmail.com.
This script queries the AWS F3(region) database for attendance records. It then generates leaderboard bar graphs
for each AO for the current month and YTD on total attendance.
The graph then is sent to each AO in a Slack message.
'''

from slacker import Slacker
import pandas as pd
import pymysql.cursors
import datetime
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import configparser
import sys

# Configure AWS credentials
config = configparser.ConfigParser()
config.read('../config/credentials.ini')
host = config['aws']['host']
port = int(config['aws']['port'])
user = config['aws']['user']
password = config['aws']['password']
#db = config['aws']['db']
db = sys.argv[1]
region = sys.argv[3]
#region = 'STL'

# Set Slack token
key = sys.argv[2]
#key = config['slack']['prod_key']
slack = Slacker(key)
firstf = sys.argv[4] #designated 1st-f channel for the region

#Define AWS Database connection criteria
mydb = pymysql.connect(
    host=host,
    port=port,
    user=user,
    password=password,
    db=db,
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor)

#Graph Counter Reset
total_graphs = 0 # Sets a counter for the total number of graphs made (users with posting data)

#Get Current Year, Month Number and Name
d = datetime.datetime.now()
thismonth = d.strftime("%m")
thismonthname = d.strftime("%b")
thismonthnamelong = d.strftime("%B")
yearnum = d.strftime("%Y")

try:
    with mydb.cursor() as cursor:
        sql = "SELECT ao FROM aos WHERE backblast = 1"
        cursor.execute(sql)
        aos = cursor.fetchall()
        aos_df = pd.DataFrame(aos, columns={'ao'})
finally:
    print('Now pulling all beatdown records... Stand by...')

total_graphs = 0 # Sets a counter for the total number of graphs made (users with posting data)

# Query AWS by for beatdown history
for ao in aos_df['ao']:
    month = []
    day = []
    year = []
    try:
        with mydb.cursor() as cursor:
            sql = "select PAX, count(Date) as Posts\
            from attendance_view \
            where MONTH(Date) = %s \
            AND YEAR(Date) = %s \
            AND ao= %s \
            group by PAX \
            order by count(Date) desc\
            limit 20"
            val = (thismonth, yearnum, ao)
            cursor.execute(sql, val)
            posts = cursor.fetchall()
            posts_df = pd.DataFrame(posts, columns={'PAX', 'Posts'})
    finally:
        print('Now pulling all posting records for', ao, '... Stand by...')

    if not posts_df.empty:
        ax = posts_df.plot.bar(x='PAX', color={"Posts" : "orange"})
        plt.title("Monthly Leaderboard - " + thismonthnamelong + ", " + yearnum)
        plt.xlabel("")
        plt.ylabel("# Posts for " + thismonthname + ", 2021")
        plt.savefig('./plots/' + db + '/PAX_Leaderboard_' + ao + thismonthname + yearnum + '.jpg', bbox_inches='tight')  # save the figure to a file
        print('Monthly Leaderboard Graph created for AO', ao, 'Sending to Slack now... hang tight!')
        slack.chat.post_message(ao, 'Hey ' + ao + "! Check out the current posting leaderboards for " + thismonthnamelong + ", " + yearnum + " as well as for Year to Date (includes all beatdowns, rucks, Qsource, etc.). Here are the top 20 posters! T-CLAPS to these HIMs. The month isn't over yet, SYITG and get on the board!")
        slack.files.upload('./plots/' + db + '/PAX_Leaderboard_' + ao + thismonthname + yearnum + '.jpg', channels=ao)
        total_graphs = total_graphs + 1
    print('Total graphs made:', total_graphs)

    try:
        with mydb.cursor() as cursor:
            sql = "select PAX, count(Date) as Posts\
            from attendance_view \
            WHERE YEAR(Date) = %s \
            AND ao = %s \
            group by PAX \
            order by count(Date) desc\
            limit 20"
            val = (yearnum, ao)
            cursor.execute(sql, val)
            posts = cursor.fetchall()
            posts_df = pd.DataFrame(posts, columns={'PAX', 'Posts'})
    finally:
        print('Now pulling all posting records for', ao, '... Stand by...')

    if not posts_df.empty:
        ax = posts_df.plot.bar(x='PAX', color={"Posts" : "green"})
        plt.title("Year to Date Leaderboard - " + yearnum)
        plt.xlabel("")
        plt.ylabel("# Posts for " + yearnum + " - Year To Date")
        plt.savefig('./plots/' + db + '/PAX_Leaderboard_YTD_' + ao + yearnum + '.jpg', bbox_inches='tight')  # save the figure to a file
        print('YTD Leaderboard Graph created for region', region, 'Sending to Slack now... hang tight!')
        slack.files.upload('./plots/' + db + '/PAX_Leaderboard_YTD_' + ao + yearnum + '.jpg', channels=ao)
        total_graphs = total_graphs + 1
print('Total graphs made:', total_graphs)