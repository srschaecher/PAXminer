#!/usr/bin/env python3
'''
This script was written by Beaker from F3STL. Questions? @srschaecher on twitter or srschaecher@gmail.com.
This script queries the AWS F3(region) database for all beatdown records. It then deposits the beatdown info and
posting history to tab delimited files on a google sheet.
'''

import pandas as pd
import pymysql.cursors
import configparser
import matplotlib
matplotlib.use('Agg')
import sys
import os
from slacker import Slacker

# Set the working directory to the directory of the script
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

# Configure AWS credentials
config = configparser.ConfigParser();
config.read('../config/credentials.ini');
#key = config['slack']['prod_key']
host = config['aws']['host']
port = int(config['aws']['port'])
user = config['aws']['user']
password = config['aws']['password']
#db = 'f3meca'
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

try:
    with mydb.cursor() as cursor:
        sql = "SELECT * FROM beatdown_info"
        cursor.execute(sql)
        bds = cursor.fetchall()
        bds_df = pd.DataFrame(bds)
finally:
    print('Now pulling all beatdown records... Stand by...')

try:
    with mydb.cursor() as cursor:
        sql2 = "SELECT * FROM attendance_view"
        cursor.execute(sql2)
        posts = cursor.fetchall()
        posts_df = pd.DataFrame(posts, columns={'Date', 'AO', 'PAX'})
finally:
    print('Now pulling all post records... Stand by...')


# saving beatdowns as a CSV file
bds_df.to_csv('/import/f3/' + db + '_Beatdowns.csv', sep =',', index=False)
posts_df.to_csv('/import/f3/' + db + '_Posts.csv', sep =',', index=False)
