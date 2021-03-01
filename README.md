<img src="https://f3nation.com/wp-content/uploads/2020/07/f3_2000x2000_circle-1024x1024-1-1024x1024-1-e1594083589231.png" align="right" />

# PAXminer
PAXminer is a set of proesses that retrieve and parse messages from an F3 unit's Slack communications channels in order to pull key information out of Backblasts and store that information in a database for recordkeeping purposes. It also automatically generates stats graphs and charts and sends those to individual PAX as well as to AOs and Regions (1st-F) to highlight monthly or yearly posting statistics.

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
Paxminer was designed to be a multi-region tool running in the cloud. Adding a new region to use PAXminer is fairly simple and straightforward. While you are welcome to download the scripts and implement your own version, you can be up and running quickly if you choose to use the existing platform. All you need to do to start is to add the app to your local Slack workspace as detailed below, then contact Beaker (F3STL) who will add your region to the workflow.

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
> Beaker can work with you to quickly replicate and create your region database schema in the existing AWS environment - or you can create your own. 
> Don't worry, I'll walk you through it all and you will be up and running in no time!



## SLACK
If you don't already have one, you will need to first create a new Slack workspace for your F3 location as a communication channel. Slack is free and highly versatile, it's a great tool to use for location communication. It has a mobile app, website, and desktop app all available for use. If you already use slack for other workspaces (Work, Church, Friends, etc...) then adding another one is trivial and you can easily switch back and forth between them.

- ["Create a New Slack Workspace"](https://slack.com/get-started#/create) - For setting up an entirely new workspace
- ["Sign in to your existing workspace"](https://slack.com/signin#/signin) - If you already have a workspace

## Create a new PAXminer app hook in Slack and make note of the security key
Don't worry, it's a lot easier than it sounds. You must have admin privileges in your Slack workspace in order to do this. The first thing you need to do is just to tell slack "hey, I have something that will need to access my Slack environment from outside of the Slack system." This is called an incoming webhook.
- From your Slack workspace, click on the workspace name dropdown menu -> Settings & Administration -> Manage Apps 
- <img src="https://manula.r.sizr.io/large/user/12398/img/slack-admin-mngapps.png" align="center" />
- Click "Build" on the top right of your screen
- Click "Create New App"
- Enter App Name = "PAXminer"
- Select your F3 Workspace
- Click "Create" and then select "Incoming Webhooks" functionality needed for your app
- Turn on the "Activate Incoming Webhooks" toggle
- Click "Add New Webhook to Workspace"
- Slack will ask you "Where should PAXminer Post?" - select #general (or any Slack channel, it doesn't matter for now. I created a temporary #debugging channel. Anything will work.
- Click "Allow"
- After creating the app, select "OAuth & Permissions" on the left side menu
- Find the "Bot User OAuth Access Token" and copy it - paste it somewhere for future use. You will add this to the "credentials.ini" file later.
- Find the PaxMiner.png image (https://github.com/srschaecher/PAXminer/blob/main/PaxMiner.png) and download. Use this to replace the app image under "Basic Information" near the bottom.
- <img src="https://user-images.githubusercontent.com/563929/82573621-94be2b00-9bb8-11ea-991c-f7ae5cfffc15.png" align="center" /> 
- Under OAuth & Permissions, scroll down to "Scope" and click "Add an OAuth Scope". This is where you will give your new PAXminer app permissions to do things within your Slack workspace. Add all of the following scopes:
> channels:history, channels:join, channels:read, chat:write, users.profile:read, users:read, users:read.email, commands, files:write, incoming-webhook, im:write, users:read.email
- After adding all listed Scope settings, Slack will ask you to "Reinstall App". This just means Slack needs to re-push the app's updated settings. Scroll up and click on "Reinstall App". If the access token changes, make sure to copy it.
- Your Slack environment is now set up for the PAXminer tool to pull messages from your Slack channels.


## Feedback
- Submit a PR with your feedback!

## Contribute

## License

[![CC0](https://licensebuttons.net/p/zero/1.0/88x31.png)](https://creativecommons.org/publicdomain/zero/1.0/)

To the extent possible under law, Scott Schaecher has waived all copyright and related or neighboring rights to this work.
