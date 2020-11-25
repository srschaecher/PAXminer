#!/usr/bin/env python
'''
This script was written by Beaker from F3STL. Questions? @srschaecher on twitter or srschaecher@gmail.com.
This script queries Slack for all PAX Users and their respective beatdown attendance. It then generates bar graphs
on total # of unique individuals that attended aeach AO.
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

print('Looking for all F3STL Slack Users. Stand by...')
# Make users Data Frame
users_response = slack.users.list()
users = users_response.body['members']
users_df = pd.json_normalize(users)
users_df = users_df[['id', 'profile.display_name', 'profile.real_name', 'profile.phone', 'profile.email']]
users_df = users_df.rename(columns={'id' : 'user_id', 'profile.display_name' : 'user_name', 'profile.real_name' : 'real_name', 'profile.phone' : 'phone', 'profile.email' : 'email'})

print('Now pulling all of those users beatdown attendance records... Stand by...')

# Query AWS by user ID for attendance history
#users_df = users_df.iloc[:10] # THIS LINE IS FOR TESTING PURPOSES, THIS FORCES ONLY n USER ROWS TO BE SENT THROUGH THE PIPE
total_graphs = 0 # Sets a counter for the total number of graphs made (users with posting data)
for user_id in users_df['user_id']:
    try:
        attendance_tmp_df = pd.DataFrame([])  # creates an empty dataframe to append to
        with mydb.cursor() as cursor:
            sql = "SELECT * FROM attendance_view WHERE PAX = (SELECT user_name FROM users WHERE user_id = %s) ORDER BY Date"
            user_id_tmp = user_id
            val = user_id_tmp
            cursor.execute(sql, val)
            attendance_tmp = cursor.fetchall()
            attendance_tmp_df = pd.DataFrame(attendance_tmp)
            month = []
            day = []
            year = []
            count = attendance_tmp_df.shape[0]
            #if user_id_tmp == 'U0187M4NWG4': #Use this to send a graph to only 1 specific PAX
            if count > 0: # This sends a graph to ALL PAX who have attended at least 1 beatdown
                for Date in attendance_tmp_df['Date']:
                #for index, row in attendance_tmp_df.iterrows():
                    datee = datetime.datetime.strptime(Date, "%Y-%m-%d")
                    month.append(datee.strftime("%B"))
                    day.append(datee.day)
                    year.append(datee.year)
                pax = attendance_tmp_df.iloc[0]['PAX']
                attendance_tmp_df['Month'] = month
                attendance_tmp_df['Day'] = day
                attendance_tmp_df['Year'] = year
                month_order = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
                attendance_tmp_df.groupby(['Month', 'AO']).size().unstack().plot(kind='bar', stacked=True)
                plt.title('Number of posts from '+ pax + ' by AO/Month')
                plt.legend(loc = 'center left', bbox_to_anchor=(1, 0.5), frameon = False)
                plt.ioff()
                plt.savefig('./plots/' + user_id_tmp + '.jpg', bbox_inches='tight') #save the figure to a file
                print('Graph created for user', pax, 'Sending to Slack now... hang tight!')
                slack.chat.post_message(user_id_tmp, 'Hello ' + pax + "! If you have received this multiple times, I am sorry, don't blame me - Beaker screwed up and didnt add the end of October correctly. It's his fault. Here is the REAL final, summary for October. Pay little attention to pre-October as those records are not complete. Lets see some more color in November! Hit up as many AOs as you can! #tasteTheRainbow")
                slack.files.upload('./plots/' + user_id_tmp + '.jpg',channels=user_id_tmp)
                total_graphs = total_graphs + 1
    finally:
        pass
print('Total graphs made:', total_graphs)
mydb.close()