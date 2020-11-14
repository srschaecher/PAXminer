#!/Users/schaecher/.pyenv/versions/3.7.3/bin/python3.7
'''
This script was written by Beaker from F3STL. Questions? @srschaecher on twitter or srschaecher@gmail.com.
This script queries the AWS F3(region) database for all beatdown records. It then generates bar graphs
on FNG's for each AO and sends it to the AO channel in a Slack message.
'''

from slacker import Slacker
import pandas as pd
import pymysql.cursors
import configparser
import datetime
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Configure Slack credentials
config = configparser.ConfigParser()
config.read('/Users/schaecher/PycharmProjects/f3Slack/credentials.ini')
key = config['slack']['prod_key']

# Configure AWS Credentials
host = config['aws']['host']
port = int(config['aws']['port'])
user = config['aws']['user']
password = config['aws']['password']
db = config['aws']['db']

# Set Slack tokens
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
        sql = "SELECT DISTINCT AO, PAX FROM attendance_view WHERE DATE like '2020-10%'"
        cursor.execute(sql)
        bd_tmp = cursor.fetchall()
        bd_tmp_df = pd.DataFrame(bd_tmp, columns={'AO', 'PAX'})
        bd_tmp_df.groupby(['AO']).size().plot(kind='bar', stacked=True)
        plt.title('Number of unique PAX attending each AO, October 2020')
        #plt.legend(loc='center left', bbox_to_anchor=(1, 0.5), frameon=False)
        plt.show()
        #plt.ioff()
        plt.savefig('./plots/PAX_Counts_By_AO_October.jpg', bbox_inches='tight')  # save the figure to a file
        #print('Graph created for AO', ao, 'Sending to Slack now... hang tight!')
        #slack.chat.post_message(user_id_tmp,
        #                        'Hello ' + pax + '! Here is a quick look at your posting stats since I started tracking (mid-Sept). If you think there are discrepancies, contact @Beaker for help. You have only 2 more days to get some October numbers in, make them count!')
        #slack.files.upload('/Users/schaecher/PycharmProjects/f3Slack/plots/' + user_id_tmp + '.jpg', channels=user_id_tmp)
        total_graphs = total_graphs + 1
finally:
    print('Total graphs made:', total_graphs)
    mydb.close()