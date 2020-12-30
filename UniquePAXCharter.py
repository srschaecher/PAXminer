#!/usr/bin/env python3
'''
This script was written by Beaker from F3STL. Questions? @srschaecher on twitter or srschaecher@gmail.com.
This script queries the AWS F3(region) database for all beatdown records. It then generates bar graphs
on total unique PAX attendance for each AO and sends it to the 1st F channel in a Slack message.
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

# Configure AWS credentials
config = configparser.ConfigParser();
config.read('../config/credentials.ini');
#key = config['slack']['prod_key']
host = config['aws']['host']
port = int(config['aws']['port'])
user = config['aws']['user']
password = config['aws']['password']
#db = config['aws']['db']
#db = sys.argv[1]
db = 'f3kc' # Set this for a specific region
region = 'KC'

# Set Slack token
#key = sys.argv[2]
key = 'xoxb-532986085797-1522344030132-OcU9uqTFXkGXqyqeclz5Wpsz'
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

total_graphs = 0 # Sets a counter for the total number of graphs made (users with posting data)

# Query AWS by for beatdown history
try:
    with mydb.cursor() as cursor:
        sql = "SELECT DISTINCT AO, MONTHNAME(Date) as Month, PAX FROM attendance_view WHERE MONTH(Date) IN (10, 11, 12)"
        cursor.execute(sql)
        bd_tmp = cursor.fetchall()
        bd_tmp_df = pd.DataFrame(bd_tmp, columns={'AO', 'Month', 'PAX'})
        bd_tmp_df.groupby(['AO', 'Month']).size().unstack().plot(kind='bar')
        plt.title('Number of unique PAX attending each AO by month')
        plt.legend(loc='center left', bbox_to_anchor=(1, 0.5), frameon=False)
        #plt.show()
        plt.ioff()
        plt.savefig('./plots/' + region + '/PAX_Counts_By_AO.jpg', bbox_inches='tight')  # save the figure to a file
        print('Graph created for unique PAX across all AOs. Sending to Slack now... hang tight!')
        slack.chat.post_message('U019BCPMD9T', "Hello " + region + "! Here is a quick look at how many UNIQUE PAX attended beatdowns by AO by Month!")
        slack.files.upload('./plots/' + region + '/PAX_Counts_By_AO.jpg', channels='U019BCPMD9T')
        total_graphs = total_graphs + 1
finally:
    print('Total graphs made:', total_graphs)
    mydb.close()