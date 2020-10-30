#!/Users/schaecher/.pyenv/bin/python3.7
'''
This script was written by Beaker from F3STL. Questions? @srschaecher on twitter or srschaecher@gmail.com.
This script queries Slack for Channels and inserts channel IDs/names into the AWS database for recordkeeping.
The Channels data table is used by PAXminer to query only AO channels for backblasts.
'''

from slacker import Slacker
import pandas as pd
import pymysql.cursors
import configparser

# Configure Slack credentials
config = configparser.ConfigParser();
config.read('/Users/schaecher/PycharmProjects/f3Slack/credentials.ini');
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

# Get channel list
channels_response = slack.conversations.list()
channels = channels_response.body['channels']
channels_df = pd.json_normalize(channels)
channels_df = channels_df[['id', 'name', 'created', 'is_archived']]
channels_df = channels_df.rename(columns={'id' : 'channel_id', 'name' : 'ao', 'created' : 'channel_created', 'is_archived' : 'archived'})

# Now connect to the AWS database and insert some rows!
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
    with mydb.cursor() as cursor2:
        sql2 = "UPDATE aos SET backblast = 1 where channel_id IN('C01B8V4ALBS','C018PAT51RA','C017QAWD9TM','C017976EV8X','C01ACC20TML','C017NJ4DVRT','C01797BQYG7','C01B0TVJY2K','C017Q4VJMH8','C0179CJ16P9','C01AR9WSDU4','C017BL7RX24','C014UM21YBU')"
        cursor2.execute(sql2)
        mydb.commit()
    with mydb.cursor() as cursor3:
        sql3 = "UPDATE aos SET backblast = 0 where backblast IS NULL"
        cursor3.execute(sql3)
        mydb.commit()
finally:
    mydb.close()