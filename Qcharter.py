#!/usr/bin/env python3
'''
This script was written by Beaker from F3STL. Questions? @srschaecher on twitter or srschaecher@gmail.com.
This script queries the AWS F3(region) database for all beatdown records. It then generates bar graphs
on Q's for each AO and sends it to the AO channel in a Slack message.
'''

from slacker import Slacker
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
    with mydb.cursor() as cursor:
        sql = "SELECT * FROM beatdown_info WHERE AO = %s AND YEAR(Date) = %s ORDER BY Date"
        val = (ao, yearnum)
        cursor.execute(sql, val)
        bd_tmp = cursor.fetchall()
        bd_tmp_df = pd.DataFrame(bd_tmp)
        if not bd_tmp_df.empty:
            for Date in bd_tmp_df['Date']:
                datee = datetime.datetime.strptime(str(Date), "%Y-%m-%d")
                month.append(datee.strftime("%B"))
                day.append(datee.day)
                year.append(datee.year)
            bd_tmp_df['Month'] = month
            bd_tmp_df['Day'] = day
            bd_tmp_df['Year'] = year
            month_order = ["January", "February", "March", "April", "May", "June", "July", "August", "September",
                           "October", "November", "December"]
            try:
                bd_tmp_df.groupby(['Month', 'Q']).size().unstack().sort_values(['Month'], ascending=False).plot(kind='bar')
                plt.title('Number of Qs by individual at ' + ao + ' by Month for ' + yearnum)
                plt.legend(loc='center left', bbox_to_anchor=(1, 0.5), frameon=False)
                plt.ioff()
                #ao = 'U0187M4NWG4' #Use this for testing to send all charts to a specific user
                plt.savefig('./plots/' + db + '/Q_Counts_' + ao + "_" + thismonthname + yearnum + '.jpg', bbox_inches='tight')  # save the figure to a file
                print('Q Graph created for AO', ao, 'Sending to Slack now... hang tight!')
                slack.chat.post_message(ao, 'Hey ' + ao + '! Here is a look at who has Qd at this AO by month. Is your name on this list? Remember Core Principle #4 - F3 is peer led on a rotating fashion. Exercise your leadership muscles. Sign up to Q!')
                slack.files.upload('./plots/' + db + '/Q_Counts_' + ao + "_" + thismonthname + yearnum + '.jpg', channels=ao)
                total_graphs = total_graphs + 1
            except:
                print('An Error Occurred in Sending')
            finally:
                print('Message Sent')
print('Total AO graphs made:', total_graphs)

try:
    total_graphs = 0
    month = []
    day = []
    year = []
    with mydb.cursor() as cursor:
        sql = "SELECT * FROM beatdown_info WHERE YEAR(Date) = %s AND MONTH(Date) = %s ORDER BY Date"
        val = (yearnum, thismonth)
        cursor.execute(sql, val)
        bd_tmp2 = cursor.fetchall()
        bd_tmp_df2 = pd.DataFrame(bd_tmp2)
        if not bd_tmp_df2.empty:
            for Date in bd_tmp_df2['Date']:
                datee = datetime.datetime.strptime(str(Date), "%Y-%m-%d")
                month.append(datee.strftime("%B"))
                day.append(datee.day)
                year.append(datee.year)
            bd_tmp_df2['Month'] = month
            bd_tmp_df2['Day'] = day
            bd_tmp_df2['Year'] = year
            bd_tmp_df2.groupby(['Q', 'AO']).size().unstack().plot(kind='bar', stacked = True, figsize=(16,4))
            #bd_tmp_df2.groupby(['Q'],['AO']).sum().size().plot(kind='bar', stacked=True, sort_columns=False, figsize=(8,4))
            plt.title('Number of Qs by individual across all AOs for ' + thismonthnamelong + ', ' + yearnum)
            plt.legend(loc='center left', bbox_to_anchor=(1, 0.5), frameon=False)
            plt.ioff()
            plt.savefig('./plots/' + db + '/Q_Counts_' + db + "_" + thismonthname + yearnum + '.jpg',
                        bbox_inches='tight')  # save the figure to a file
            print('Q Graph created for ', region, 'Sending to Slack now... hang tight!')
            slack.chat.post_message(firstf, 'Hey ' + region + '! Here is a look at who has Qd across all AOs by month. Is your name on this list? Remember Core Principle #4 - F3 is peer led on a rotating fashion. Exercise your leadership muscles. Sign up to Q!')
            slack.files.upload('./plots/' + db + '/Q_Counts_' + db + "_" + thismonthname + yearnum + '.jpg',
                               channels=firstf)
            total_graphs = total_graphs + 1
finally:
    print('Total Q summary graphs made:', total_graphs)