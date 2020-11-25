#!/usr/bin/env python
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
import sys

# Configure AWS credentials
config = configparser.ConfigParser();
config.read('../config/credentials.ini');
#key = config['slack']['prod_key']
host = config['aws']['host']
port = int(config['aws']['port'])
user = config['aws']['user']
password = config['aws']['password']
#db = config['aws']['db']
db = sys.argv[1]

# Set Slack tokens
key = sys.argv[2]
slack = Slacker(key)

#Define AWS Database connection criteria
mydb = pymysql.connect(
    host=host,
    port=port,
    user=user,
    password=password,
    db=db,
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor)

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
try:
    for ao in aos_df['ao']:
        month = []
        day = []
        year = []
        with mydb.cursor() as cursor:
            sql = "SELECT * FROM beatdown_info WHERE ao = %s"
            val = (ao)
            cursor.execute(sql, val)
            bd_tmp = cursor.fetchall()
            bd_tmp_df = pd.DataFrame(bd_tmp, columns={'Date', 'AO', 'Q', 'CoQ', 'pax_count', 'fngs', 'fng_count'})
            for Date in bd_tmp_df['Date']:
                datee = datetime.datetime.strptime(str(Date), "%Y-%m-%d")
                month.append(datee.strftime("%B"))
                day.append(datee.day)
                year.append(datee.year)
            bd_tmp_df['Month'] = month
            bd_tmp_df['Day'] = day
            bd_tmp_df['Year'] = year
            bd_tmp_df = bd_tmp_df[bd_tmp_df.Month == 'October'] # Keep only October data until I can better figure out how to facet the charts by month
            bd_tmp_df.groupby(['Q', 'Month']).size().unstack().plot(kind='bar', stacked=True)
            plt.title('Number of Qs by individual at ' + ao + ' by Month')
            plt.legend(loc='center left', bbox_to_anchor=(1, 0.5), frameon=False)
            plt.ioff()
            plt.savefig('./plots/Q_Counts_' + ao + '.jpg', bbox_inches='tight')  # save the figure to a file
            print('Graph created for AO', ao, 'Sending to Slack now... hang tight!')
        #slack.chat.post_message(user_id_tmp,
        #                        'Hello ' + pax + '! Here is a quick look at your posting stats since I started tracking (mid-Sept). If you think there are discrepancies, contact @Beaker for help. You have only 2 more days to get some October numbers in, make them count!')
        #slack.files.upload('/Users/schaecher/PycharmProjects/f3Slack/plots/' + user_id_tmp + '.jpg', channels=user_id_tmp)
        total_graphs = total_graphs + 1
finally:
    print('Total graphs made:', total_graphs)
    mydb.close()