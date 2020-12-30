#!/usr/bin/env python3
'''
This script was written by Beaker from F3STL. Questions? @srschaecher on twitter or srschaecher@gmail.com.
This script queries Slack for all PAX Users and inserts User IDs/names into the AWS database for recordkeeping.
Updates existing user records if changes have been made. Uses parameterized inputs for multiple region updates.

Usage: F3SlackUserLister.py [db_name] [slack_token]

'''

from slacker import Slacker
import pandas as pd
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

print('Looking for any new or updated F3 Slack Users. Stand by...')

# Make users Data Frame
users_response = slack.users.list()
users = users_response.body['members']
users_df = pd.json_normalize(users)
users_df = users_df[['id', 'profile.display_name', 'profile.real_name', 'profile.phone', 'profile.email']]
users_df = users_df.rename(columns={'id' : 'user_id', 'profile.display_name' : 'user_name', 'profile.real_name' : 'real_name', 'profile.phone' : 'phone', 'profile.email' : 'email'})
# Update any null user_names with the real_name values
for index, row in users_df.iterrows():
    un_tmp = row['user_name']
    rn_tmp = row['real_name']
    em_tmp = row['email']
    if un_tmp == "" :
        row['user_name'] = rn_tmp
users_df['email'].fillna("None", inplace=True)

# Now connect to the AWS database and insert some rows!
try:
    with mydb.cursor() as cursor:
        for index, row in users_df.iterrows():
            sql = "INSERT INTO users (user_id, user_name, real_name, phone, email) VALUES (%s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE user_name=%s, real_name=%s, phone=%s, email=%s"
            user_id_tmp = row['user_id']
            user_name_tmp = row['user_name']
            real_name_tmp = row['real_name']
            phone_tmp = row['phone']
            email_tmp = row['email']
            val = (user_id_tmp, user_name_tmp, real_name_tmp, phone_tmp, email_tmp, user_name_tmp, real_name_tmp, phone_tmp, email_tmp)
            cursor.execute(sql, val)
            mydb.commit()
            result = cursor.rowcount
            if result == 1:
                print("Record inserted for user", user_name_tmp)
            elif result == 2:
                print("Record updated for user", user_name_tmp)

finally:
    mydb.close()
print('Finished - users are up to date.')
