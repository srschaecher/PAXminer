#!/usr/bin/env python3
'''
This script was written by Beaker from F3STL. Questions? @srschaecher on twitter or srschaecher@gmail.com.
This script queries the AWS F3(region) database for all beatdown records. It then generates a table of summary stats
on total posts and beatdowns for each AO and sends it to the 1st F channel in a Slack message.
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
import sys
import dataframe_image as dfi
import seaborn as sns
import plotly.figure_factory as ff

# Configure AWS credentials
config = configparser.ConfigParser();
config.read('../config/credentials.ini');
host = config['aws']['host']
port = int(config['aws']['port'])
user = config['aws']['user']
password = config['aws']['password']
#db = config['aws']['db']
db = sys.argv[1]
region = sys.argv[3]

# Set Slack token
key = sys.argv[2]
#key = config['slack']['prod_key']
slack = Slacker(key)
firstf = sys.argv[4] #parameter input for designated 1st-f channel for the region

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

#Get Current Year, Month Number and Name
d = datetime.datetime.now()
thismonth = d.strftime("%m")
thismonthname = d.strftime("%b")
thismonthnamelong = d.strftime("%B")
yearnum = d.strftime("%Y")

#Define colormap for table
cm = sns.light_palette("green", as_cmap=True)

# Query AWS by for beatdown history
try:
    with mydb.cursor() as cursor:
        sql = "select av.AO, x.TotalPax as TotalPax, count(distinct av.PAX) as TotalUniquePax, count(Distinct av.Date) as BDs, Round(x.TotalPax/count(Distinct av.Date),1) as AvgAttendance,sum(Distinct bd.fng_count) as TotalFNGs, MONTH(av.Date) as Month,Year(av.date) as Year \
        from attendance_view av \
        left outer join beatdown_info bd on bd.AO = av.ao and bd.date = av.Date \
        left outer join (select sum(pax_count) as TotalPax, AO, month(Date) as month, year(Date) as Year from beatdown_info GROUP BY year, month, AO) x on x.AO = av.AO and x.month=(month(av.date)) and x.year = (year(av.date)) \
        WHERE Year = %s \
        GROUP BY year, Month, AO \
        order by Year desc, Month desc, Round(x.TotalPax/count(Distinct av.Date),1) desc"
        val = yearnum
        cursor.execute(sql,val)
        bd_tmp = cursor.fetchall()
        bd_tmp_df = pd.DataFrame(bd_tmp)
        bd_tmp_df['Month'] = bd_tmp_df['Month'].replace([1,2,3,4,5,6,7,8,9,10,11,12], ['January','February','March','April','May','June','July','August','September','October','November','December'])
        bd_df_styled = bd_tmp_df.style.background_gradient(cmap=cm, subset=['TotalPax', 'TotalUniquePax']).set_caption("This region is ON FIRE!")
        dfi.export(bd_df_styled, './plots/' + db + '/AO_SummaryTable' + thismonthname + yearnum + '.jpg')  # save the figure to a file
        #fig = ff.create_table(bd_df_styled)
        #fig.write_image('./plots/' + db + '/AO_SummaryTable' + thismonthname + yearnum + '.jpg')
        print('AO summary table created for all AOs. Sending to Slack now... hang tight!')
        slack.chat.post_message(firstf, "Hello " + region + "! Here is a detailed summary of AO posting stats for the region in " + yearnum + "!")
        slack.files.upload('./plots/' + db + '/AO_SummaryTable' + thismonthname + yearnum + '.jpg', channels=firstf)
        total_graphs = total_graphs + 1
finally:
    print('Total graphs made:', total_graphs)
    mydb.close()