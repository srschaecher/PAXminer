<img src="https://f3nation.com/wp-content/uploads/2020/07/f3_2000x2000_circle-1024x1024-1-1024x1024-1-e1594083589231.png" align="right" />

# PAXminer
PAXminer is a set of processes that retrieve and parse messages from an F3 region's Slack communications channels in order to capture Backblasts, pull key information out of Backblasts and store that information in a database for recordkeeping purposes. It also automatically generates stats graphs and charts and sends those to individual PAX as well as to AOs and Regions (1st-F) to highlight monthly or yearly posting statistics.

PAXminer pulls the following infomation from Backblasts and sends it to a shared database in AWS RDS (Amazon Web Services - Relational Database Service). Each region using PAXminer gets a dedicated schema for their data.

- AO
- Date of the Beatdown
- Who was the Q
- Was there a Co-Q?
- What PAX attended?
- How many attended in total?
- Any FNGs?

This tool started out with me saying "there HAS to be a beter way to do this" as we were collecting our F3 posting stats manually in Excel. We are adding new things to the process every day! The more regions that get involved, the better and more standardized we can make it! All collaboration is welcome!



## Setting up a new region to use PAXminer
For instructions on getting your F3 region up and running with PAXminer, start here: https://f3stlouis.com/paxminer/

## Files
- *F3SlackChannelLister.py* : Pulls all channel information from the Slack workspace and inserts/updates the info in the database. Channel info is required for the rest of the processes.
- *F3SlackUserLister.py* : Python script that pulls all PAX user info from Slack and inserts it into the database. User info is required for the rest of the processes.
- *BDminer.py* : Python script that pulls Beatdown specific information and sends to the database (date, AO, Q, Co-Q, Count, FNGs, etc)
- *PAXminer.py* : Python script that finds all backblasts from AO channels (including rucking, blackops) and parses them for all of the PAX in attendance. Inserts all attendance records into the database.
- *PAXminer_Daily_Execution.py* : Python script that is used for automating the daily backblast mining and data capture. This process first pulls a list of all F3 regions using PAXminer, and then runs the above scripts for each of their Slack environments. The resulting data gets put into each region's database tables.
- *PAXcharter.py* : Python script that creates individual bar charts for every user who has attended a beatdown, showing # of posts by AO by month. Sends charts as direct messages to each user in Slack. Intended to run monthly.
- *Qcharter.py* : Python script that creates histograms for each AO that shows who has Q'd and how many times by month. Sends charts as messages to each AO channel in Slack. Intended to run monthly.
- *AOcharter.py* : Python script that creates a histogram of AO specific stats (# of posts) by month and sends to the AO slack channel. Intended to run monthly.
- *f3stl_mysql.mwb* : MySQL Database schema to implement the database.
- *FNGcharter.py* : Python script that creates a histogram of FNG counts by AO. Intended to run monthly.
- *credeintials_template.ini* : Required file that contains AWS access tokens. This is managed by the PAXminer admin, nothing you need to do unless you choose to run PAXminer on your own. If so, you will need to add your unique access info, save as credentials.ini, and ensure you re-point the scripts to your credentials.ini file.
- *Backblast_Template.doc* : Standard template for Qs to use with backblast posts. This template is parsed by the scripts to find pertinent backblast info. The template must be followed or the scripts will not find the requisite info.
- *LICENSE* : GNU Public License
- *README.md* : This readme

## Examples
Tracking this information lets you ask many different questions about your F3 attendance patterns, such as:
- How many times has Beaker (that's me) attended a beatdown this week/month/year? 
- What AO does Beaker most often attend?
- What days of the week are busiest across all AOs?
- Is attendance high or low when a specific person Qs?
- How many times did GMO (the F3STL Naantan) Q'd last month?
- Who are our Cotters that we need to reach out to? PAX that have been MIA for a while?
- Is it time to open a new AO?
- and the list goes on...

## Prerequisites
> There are some prerequisites you will need to set up first, including creating a SLACK workspace for your F3 group.
> Beaker can work with you to quickly get you up and running on the multi-region setup, no need for you to configure and run everything up on your own.



## SLACK
If you don't already have one, you will need to first create a new Slack workspace for your F3 location as a communication channel. Slack is free and highly versatile, it's a great tool to use for location communication. It has a mobile app, website, and desktop app all available for use. If you already use slack for other workspaces (Work, Church, Friends, etc...) then adding another one is trivial and you can easily switch back and forth between them.

- ["Create a New Slack Workspace"](https://slack.com/get-started#/create) - For setting up an entirely new workspace
- ["Sign in to your existing workspace"](https://slack.com/signin#/signin) - If you already have a workspace

## Feedback
- Submit a PR with your feedback!

## Contribute

## License

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.

