#!/usr/bin/env python3
'''
This script was written by Beaker from F3STL. Questions? @srschaecher on twitter or srschaecher@gmail.com.
This script queries Slack for all PAX Users and their respective beatdown attendance. It then generates bar graphs
on attendance for each member and sends it to them in a private Slack message.
'''

from slack_sdk import WebClient
import pandas as pd
import pymysql.cursors
import configparser
import datetime
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import sys
import time
import os

# Configure AWS credentials
config = configparser.ConfigParser();
config.read('../config/credentials.ini');
host = config['aws']['host']
port = int(config['aws']['port'])
user = config['aws']['user']
password = config['aws']['password']
#db = config['aws']['db']
db = sys.argv[1]

# Set Slack token
key = sys.argv[2]
slack = WebClient(token=key)

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
d = d - datetime.timedelta(days=3)
thismonth = d.strftime("%m")
thismonthname = d.strftime("%b")
thismonthnamelong = d.strftime("%B")
yearnum = d.strftime("%Y")

print('Looking for all Slack Users for ' + db + '. Stand by...')

# Make users Data Frame
column_names = ['user_id', 'user_name', 'real_name']
users_df = pd.DataFrame(columns = column_names)
data = ''
while True:
    users_response = slack.users_list(limit=1000, cursor=data)
    response_metadata = users_response.get('response_metadata', {})
    next_cursor = response_metadata.get('next_cursor')
    users = users_response.data['members']
    users_df_tmp = pd.json_normalize(users)
    users_df_tmp = users_df_tmp[['id', 'profile.display_name', 'profile.real_name']]
    users_df_tmp = users_df_tmp.rename(columns={'id' : 'user_id', 'profile.display_name' : 'user_name', 'profile.real_name' : 'real_name'})
    users_df = users_df.append(users_df_tmp, ignore_index=True)
    if next_cursor:
        # Keep going from next offset.
        #print('next_cursor =' + next_cursor)
        data = next_cursor
    else:
        break
for index, row in users_df.iterrows():
    un_tmp = row['user_name']
    rn_tmp = row['real_name']
    if un_tmp == "" :
        row['user_name'] = rn_tmp

print('Now pulling all of those users beatdown attendance records... Stand by...')

# Query AWS by user ID for attendance history
#users_df = users_df.iloc[:10] # THIS LINE IS FOR TESTING PURPOSES, THIS FORCES ONLY n USER ROWS TO BE SENT THROUGH THE PIPE
total_graphs = 0 # Sets a counter for the total number of graphs made (users with posting data)
pause_on = [ 50, 100, 150, 200, 250, 300, 350, 400 ]

for user_id in users_df['user_id']:
    try:
        attendance_tmp_df = pd.DataFrame([])  # creates an empty dataframe to append to
        with mydb.cursor() as cursor:
                sql = "SELECT * FROM attendance_view WHERE PAX = (SELECT user_name FROM users WHERE user_id = %s) AND YEAR(Date) = %s ORDER BY Date"
                user_id_tmp = user_id
                val = (user_id_tmp, yearnum)
                cursor.execute(sql, val)
                attendance_tmp = cursor.fetchall()
                attendance_tmp_df = pd.DataFrame(attendance_tmp)
                month = []
                day = []
                year = []
                count = attendance_tmp_df.shape[0]
                if (total_graphs in pause_on):
                    time.sleep(20)
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
                    attendance_tmp_df.sort_values(by=['Month'], inplace = True)
                    month_order = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
                    attendance_tmp_df.groupby(['Month', 'AO']).size().unstack().sort_values(['Month'], ascending=False).plot(kind='bar', stacked=True)
                    plt.title('Number of posts from '+ pax + ' by AO/Month for ' + yearnum)
                    plt.legend(loc = 'center left', bbox_to_anchor=(1, 0.5), frameon = False)
                    plt.ioff()
                    plt.savefig('./plots/' + db + '/' + user_id_tmp + "_" + thismonthname + yearnum + '.jpg', bbox_inches='tight') #save the figure to a file
                    total_graphs = total_graphs + 1
                    #manual_graphs = [240,241,242,244,245,246,247,249,250]
                    if total_graphs > 0: # This is a count of total users processed, in case of error during processing. Set the total_graphs > to whatever # comes next in the log file row count.
                        print(total_graphs, 'PAX posting graph created for user', pax, 'Sending to Slack now... hang tight!')
                        #slack.chat.post_message(user_id_tmp, 'Hey ' + pax + "! Here is your monthly posting summary for " + yearnum + ". \nPush yourself, get those bars higher every month! SYITG!")
                        slack.files_upload(channels=user_id_tmp, initial_comment='Hey ' + pax + "! Here is your monthly posting summary for " + yearnum + ". \nPush yourself, get those bars higher every month! SYITG!", file='./plots/' + db + '/' + user_id_tmp + "_" + thismonthname + yearnum + '.jpg')
                        attendance_tmp_df.hist()
                        os.system("echo " + user_id_tmp + " >>" + "./logs/" + db + "/PAXcharter.log")
                    else:
                        print(pax + 'skipped')
    except:
            print("An exception occurred")
    finally:
        plt.close('all') #Note - this was added after the December 2020 processing, make sure this works
print('Total graphs made:', total_graphs)
mydb.close()