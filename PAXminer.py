#!/usr/bin/env python
'''
This script was written by Beaker from F3STL. Questions? @srschaecher on twitter or srschaecher@gmail.com.
This script queries Slack for User, Channel, and Conversation (channel) history and then parses all conversations to find Backblasts.
All Backblasts are then parsed to collect the PAX that attend any given workout and puts those attendance records into the AWS database for recordkeeping.
'''

import warnings
from slacker import Slacker
from datetime import datetime, timedelta
import pandas as pd
import pytz
import re
import pymysql.cursors
import configparser
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

# Set Slack token
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

# Set epoch and yesterday's timestamp for datetime calculations
epoch = datetime(1970, 1, 1)
yesterday = datetime.now() - timedelta(days = 1)
oldest = yesterday.timestamp()

# Send a message to #general channel to make sure script is working :)
#slack.chat.post_message('#general', 'Don't mind me, I'm debugging PAXminer again!')

# Make users Data Frame
users_response = slack.users.list()
users = users_response.body['members']
users_df = pd.json_normalize(users)
users_df = users_df[['id', 'profile.display_name', 'profile.real_name']]
users_df = users_df.rename(columns={'id' : 'user_id', 'profile.display_name' : 'user_name', 'profile.real_name' : 'real_name'})
for index, row in users_df.iterrows():
    un_tmp = row['user_name']
    rn_tmp = row['real_name']
    if un_tmp == "" :
        row['user_name'] = rn_tmp

'''
# Get channel list from Slack (note - this has been replaced with a channel list from the AWS database)
channels_response = slack.conversations.list()
channels = channels_response.body['channels']
channels_df = pd.json_normalize(channels)
channels_df = channels_df[['id', 'name', 'created', 'is_archived']]
channels_df = channels_df.rename(columns={'id' : 'channel_id', 'name' : 'channel_name', 'created' : 'channel_created', 'is_archived' : 'archived'})
'''

# Retrieve Channel List from AWS database (backblast = 1 denotes which channels to search for backblasts)
try:
    with mydb.cursor() as cursor:
        sql = "SELECT channel_id, ao FROM aos WHERE backblast = 1 and archived = 0"
        cursor.execute(sql)
        channels = cursor.fetchall()
        channels_df = pd.DataFrame(channels, columns={'channel_id', 'ao'})
finally:
    print('Finding all PAX that attended recent workouts - stand by.')

# Get all channel conversation
messages_df = pd.DataFrame([]) #creates an empty dataframe to append to
for id in channels_df['channel_id']:
    # print("Checking channel " + id) # <-- Use this if debugging any slack channels throwing errors
    response = slack.conversations.history(id)
    messages = response.body['messages']
    temp_df = pd.json_normalize(messages)
    temp_df = temp_df[['user', 'type', 'text', 'ts']]
    temp_df = temp_df.rename(columns={'user' : 'user_id', 'type' : 'message_type', 'ts' : 'timestamp'})
    temp_df["channel_id"] = id
    messages_df = messages_df.append(temp_df, ignore_index=True)

# Calculate Date and Time columns
msg_date = []
msg_time = []
for ts in messages_df['timestamp']:
        seconds_since_epoch = float(ts)
        datetime = epoch + timedelta(seconds=seconds_since_epoch)
        datetime = datetime.replace(tzinfo=pytz.utc)
        datetime = datetime.astimezone(pytz.timezone('America/Chicago'))
        msg_date.append(datetime.strftime('%Y-%m-%d'))
        msg_time.append(datetime.strftime('%H:%M:%S'))
messages_df['date'] = msg_date
messages_df['time'] = msg_time

# Merge the data frames into 1 joined DF
f3_df = pd.merge(messages_df, users_df)
f3_df = pd.merge(f3_df,channels_df)
f3_df = f3_df[['timestamp', 'date', 'time', 'channel_id', 'ao', 'user_id', 'user_name', 'real_name', 'text']]

# Now find only backblast messages (either "Backblast" or "Back Blast") - note .casefold() denotes case insensitivity - and pull out the PAX user ID's identified within
# This pattern finds username links followed by commas: pat = r'(?<=\\xa0).+?(?=,)'
pat = r'(?<=\<).+?(?=>)' # This pattern finds username links within brackets <>
pax_attendance_df = pd.DataFrame([])
warnings.filterwarnings("ignore", category=DeprecationWarning) #This prevents displaying the Deprecation Warning that is present for the RegEx lookahead function used below

def list_pax():
    #paxline = [line for line in text_tmp.split('\n') if 'pax'.casefold() in line.casefold()]
    paxline = re.findall(r'(?<=\n)\*?(?i)PAX\*?:\*?.+?(?=\n)', str(text_tmp), re.MULTILINE) #This is a case insensitive regex looking for \nPAX with or without an * before PAX
    #print(paxline)
    pax = re.findall(pat, str(paxline), re.MULTILINE)
    pax = [re.sub(r'@','', i) for i in pax]
    if pax:
        global pax_attendance_df
        #print(pax)
        df = pd.DataFrame(pax)
        df.columns =['user_id']
        df['ao'] = ao_tmp
        df['date'] = date_tmp
        pax_attendance_df = pax_attendance_df.append(df)

# Iterate through the new f3_df dataframe, pull out the channel_name, date, and text line from Slack. Process the text line to find the Pax list
for index, row in f3_df.iterrows():
    ao_tmp = row['channel_id']
    date_tmp = row['date']
    text_tmp = row['text']
    if re.findall('^Backblast', text_tmp, re.IGNORECASE|re.MULTILINE):
        list_pax()
    elif re.findall('^Back blast', text_tmp, re.IGNORECASE|re.MULTILINE):
        list_pax()
    elif re.findall('^Slackblast', text_tmp, re.IGNORECASE|re.MULTILINE):
        list_pax()
    elif re.findall('^\*Backblast', text_tmp, re.IGNORECASE|re.MULTILINE):
        list_pax()
    elif re.findall('^\*Back blast', text_tmp, re.IGNORECASE|re.MULTILINE):
        list_pax()
    elif re.findall('^\*Slackblast', text_tmp, re.IGNORECASE|re.MULTILINE):
        list_pax()

# Now connect to the AWS database and insert some rows!
try:
    with mydb.cursor() as cursor:
        for index, row in pax_attendance_df.iterrows():
            sql = "INSERT IGNORE INTO bd_attendance (user_id, ao_id, date) VALUES (%s, %s, %s)"
            user_id_tmp = row['user_id']
            ao_tmp = row['ao']
            date_tmp = row['date']
            val = (user_id_tmp, ao_tmp, date_tmp)
            cursor.execute(sql, val)
            mydb.commit()
            if cursor.rowcount > 0:
                print(cursor.rowcount, "record inserted for", user_id_tmp, "at", ao_tmp, "on", date_tmp)

finally:
    mydb.close()
print('Finished. You may go back to your day!')