#!/usr/bin/env python3
'''
This script was written by Beaker from F3STL. Questions? @srschaecher on twitter or srschaecher@gmail.com.
This script queries the AWS F3(region) database for attendance records. It then generates leaderboard bar graphs
for each region across all AOs for the current month and YTD on total attendance.
The graph then is sent it to the 1st F channel in a Slack message.
'''

from slack_sdk import WebClient
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
slack = WebClient(token=key)
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
d = d - datetime.timedelta(days=6)
thismonth = d.strftime("%m")
thismonthname = d.strftime("%b")
thismonthnamelong = d.strftime("%B")
yearnum = d.strftime("%Y")

try:
    with mydb.cursor() as cursor:
        sql = "select PAX, count(distinct AO) as UniqueAOs, count(Date) as Posts\
        from attendance_view \
        where MONTH(Date) = %s \
        AND YEAR(Date) = %s \
        group by PAX \
        order by count(Date) desc\
        limit 20"
        val = (thismonth, yearnum)
        cursor.execute(sql, val)
        posts = cursor.fetchall()
        posts_df = pd.DataFrame(posts, columns={'PAX', 'UniqueAOs', 'Posts'})
finally:
    print('Now pulling all posting records for', region, '... Stand by...')

if not posts_df.empty:
    ax = posts_df.plot.bar(x='PAX', color={'UniqueAOs' : "blue", "Posts" : "orange"})
    plt.title("Monthly Leaderboard - " + thismonthnamelong + ", " + yearnum)
    plt.xlabel("")
    plt.ylabel("# Posts for " + thismonthname + ", 2021")
    plt.savefig('./plots/' + db + '/PAX_Leaderboard_' + region + thismonthname + yearnum + '.jpg', bbox_inches='tight')  # save the figure to a file
    print('Monthly Leaderboard Graph created for region', region, 'Sending to Slack now... hang tight!')
    #slack.chat.post_message(firstf, 'Hey ' + region + "! Check out the current posting leaderboards for " + thismonthnamelong + ", " + yearnum + " as well as for Year to Date (includes all beatdowns, rucks, Qsource, etc.). Here are the top 20 posters! T-CLAPS to these HIMs. The month isn't over yet, SYITG and get on the board!")
    slack.files_upload(channels=firstf, initial_comment='Hey ' + region + "! Check out the current posting leaderboards for " + thismonthnamelong + ", " + yearnum + " as well as for Year to Date (includes all beatdowns, rucks, Qsource, etc.). Here are the top 20 posters! T-CLAPS to these HIMs. The month isn't over yet, SYITG and get on the board!", file='./plots/' + db + '/PAX_Leaderboard_' + region + thismonthname + yearnum + '.jpg', )
    total_graphs = total_graphs + 1
print('Total graphs made:', total_graphs)

try:
    with mydb.cursor() as cursor:
        sql = "select PAX, count(distinct AO) as UniqueAOs, count(Date) as Posts\
        from attendance_view \
        WHERE YEAR(Date) = %s \
        group by PAX \
        order by count(Date) desc\
        limit 20"
        val = (yearnum)
        cursor.execute(sql, val)
        posts = cursor.fetchall()
        posts_df = pd.DataFrame(posts, columns={'PAX', 'UniqueAOs', 'Posts'})
finally:
    print('Now pulling all posting records for', region, '... Stand by...')

if not posts_df.empty:
    ax = posts_df.plot.bar(x='PAX', color={'UniqueAOs' : "purple", "Posts" : "green"})
    plt.title("Year to Date Leaderboard - " + yearnum)
    plt.xlabel("")
    plt.ylabel("# Posts for " + yearnum + " - Year To Date")
    plt.savefig('./plots/' + db + '/PAX_Leaderboard_YTD_' + region + yearnum + '.jpg', bbox_inches='tight')  # save the figure to a file
    print('YTD Leaderboard Graph created for region', region, 'Sending to Slack now... hang tight!')
    slack.files_upload(file='./plots/' + db + '/PAX_Leaderboard_YTD_' + region + yearnum + '.jpg', channels=firstf)
    total_graphs = total_graphs + 1
print('Total graphs made:', total_graphs)