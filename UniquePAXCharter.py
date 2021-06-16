#!/usr/bin/env python3
'''
This script was written by Beaker from F3STL. Questions? @srschaecher on twitter or srschaecher@gmail.com.
This script queries the AWS F3(region) database for all beatdown records. It then generates bar graphs
on total unique PAX attendance for each AO and sends it to the 1st F channel in a Slack message.
'''

from slack_sdk import WebClient
import pandas as pd
import pymysql.cursors
import configparser
import datetime
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import configparser
import sys

# Configure AWS credentials
config = configparser.ConfigParser();
config.read('../config/credentials.ini');
host = config['aws']['host']
port = int(config['aws']['port'])
user = config['aws']['user']
password = config['aws']['password']
#db = config['aws']['db']
db = sys.argv[1]
region = sys.argv[3]

# Set Slack token
key = sys.argv[2]
slack = WebClient(token=key)
#firstf = sys.argv[4] #parameter input for designated 1st-f channel for the region
firstf = 'U0187M4NWG4' #use this for testing messages to a specific user

#Define AWS Database connection criteria
mydb = pymysql.connect(
    host=host,
    port=port,
    user=user,
    password=password,
    db=db,
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor)

total_graphs = 0 # Sets a counter for the total number of graphs made (users with posting data)

#Get Current Year, Month Number and Name
d = datetime.datetime.now()
d = d - datetime.timedelta(days=3)
thismonth = d.strftime("%m")
thismonthname = d.strftime("%b")
thismonthnamelong = d.strftime("%B")
yearnum = d.strftime("%Y")

# Query AWS by for beatdown history
try:
    with mydb.cursor() as cursor:
        sql = "SELECT DISTINCT AO, MONTHNAME(Date) as Month, PAX FROM attendance_view WHERE YEAR(Date) = %s"
        val = yearnum
        cursor.execute(sql,val)
        bd_tmp = cursor.fetchall()
        bd_tmp_df = pd.DataFrame(bd_tmp, columns={'AO', 'Month', 'PAX'})
        bd_tmp_df.groupby(['AO', 'Month']).size().unstack().plot(kind='bar')
        plt.title('Number of unique PAX attending each AO by month in ' + yearnum)
        plt.legend(loc='center left', bbox_to_anchor=(1, 0.5), frameon=False)
        plt.ioff()
        plt.savefig('./plots/' + db + '/PAX_Counts_By_AO_' + thismonthname + yearnum + '.jpg', bbox_inches='tight')  # save the figure to a file
        print('Unique PAX graph created for unique PAX across all AOs. Sending to Slack now... hang tight!')
        #slack.chat.post_message(firstf, "Hello " + region + "! Here is a quick look at how many UNIQUE PAX attended beatdowns by AO by Month for " + yearnum + "!")
        slack.files_upload(channels=firstf, initial_comment="Hello " + region + "! Here is a quick look at how many UNIQUE PAX attended beatdowns by AO by Month for " + yearnum + "!", file='./plots/' + db + '/PAX_Counts_By_AO_' + thismonthname + yearnum + '.jpg')
        total_graphs = total_graphs + 1
finally:
    print('Total graphs made:', total_graphs)
    mydb.close()