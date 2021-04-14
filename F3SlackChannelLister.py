#!/usr/bin/env python3
'''
This script was written by Beaker from F3STL. Questions? @srschaecher on twitter or srschaecher@gmail.com.
This script queries Slack for Channels and inserts channel IDs/names into the AWS database for recordkeeping.
The Channels data table is used by PAXminer to query only AO channels for backblasts. Uses parameterized inputs for
multiple region updates.

Usage: F3SlackChannelLister.py [db_name] [slack_token]
'''

import pandas as pd
import pymysql.cursors
import configparser
import sys
from slack_sdk import WebClient

# Configure AWS credentials
config = configparser.ConfigParser();
config.read('../config/credentials.ini');
host = config['aws']['host']
port = int(config['aws']['port'])
user = config['aws']['user']
password = config['aws']['password']
db = sys.argv[1]

# Set Slack tokens
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

# Get channel list
channels_response = slack.conversations_list(limit=999)
channels = channels_response.data['channels']
channels_df = pd.json_normalize(channels)
channels_df = channels_df[['id', 'name', 'created', 'is_archived']]
channels_df = channels_df.rename(columns={'id' : 'channel_id', 'name' : 'ao', 'created' : 'channel_created', 'is_archived' : 'archived'})

# Now connect to the AWS database and insert some rows!
print('Updating Slack channel list / AOs for region...')
try:
    with mydb.cursor() as cursor:
        for index, row in channels_df.iterrows():
            sql = "INSERT INTO aos (ao, channel_id, channel_created, archived) VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE ao=%s, archived=%s"
            channel_name_tmp = row['ao']
            channel_id_tmp = row['channel_id']
            channel_created_tmp = row['channel_created']
            archived_tmp = row['archived']
            val = (channel_name_tmp, channel_id_tmp, channel_created_tmp, archived_tmp, channel_name_tmp, archived_tmp)
            cursor.execute(sql, val)
            mydb.commit()
            if cursor.rowcount == 1:
                print(channel_name_tmp, "record inserted.")
            elif cursor.rowcount == 2:
                print(channel_name_tmp, "record updated.")
    with mydb.cursor() as cursor3:
        sql3 = "UPDATE aos SET backblast = 0 where backblast IS NULL"
        cursor3.execute(sql3)
        mydb.commit()
    #with mydb.cursor() as cursor4:
    #    sql4 = "UPDATE aos SET backblast = 1 where ao LIKE 'ao%' AND archived = 0 OR ao = 'general' OR ao = 'rucking' OR ao = 'blackops' OR ao = 'qsource' OR ao = 'f3-dads-2-point-0-saturday-beatdown'"
    #    cursor4.execute(sql4)
    #    mydb.commit()
finally:
    mydb.close()