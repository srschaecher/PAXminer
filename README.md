<img src="https://f3nation.com/wp-content/uploads/2020/07/f3_2000x2000_circle-1024x1024-1-1024x1024-1-e1594083589231.png" align="right" />

# PAXminer
PAXminer is a set of scripts that retrieve and parse messages from an F3 unit's Slack communications channels in order to pull key information out of Backblasts and store that information in a database for recordkeeping purposes. PAXminer pulls the following infomation from Backblasts and sends it to a database you will manage in AWS RDS (Amazon Web Services - Relational Database Service).

- AO
- Date of the Beatdown
- Who was the Q
- Was there a Co-Q?
- What PAX attended?
- How many attended in total?
- Any FNGs?

Tracking this information lets you ask many different questions about your F3 attendance patterns, such as:

## Examples

- How many times has Beaker (that's me) attended a beatdown this week/month/year? 
- What AO does Beaker most often attend?
- What days of the week are busiest across all AOs?
- Is attendance high or low when a specific person Qs?
- How many times did GMO (the F3STL Naantan) Q'd last month?
- Who are our Cotters that we need to reach out to? PAX that have been MIA for a while?
- Is it time to open a new AO?
- and the list goes on...

## Prerequisites
> There are some prerequisites you will need to set up first, including creating a SLACK workspace for your F3 group and launching a (free) Amazon AWS database.
> Don't worry, I'll walk you through it all and you will be up and running in no time!

*Note - at this time, the AWS free database tier is free for 1 year. After that, you will either have to start paying for it, create a new one, or migrate it somewhere else. Migration is easy, I'll post recommendations here when we get closer to our year expiring on what solution we will move to. Given how easy and fast AWS is to get started, I highly recommend using it to start so it will not be your bottleneck and moving it elsewhere after a year when you are more comfortable.*


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
- <img src="https://user-images.githubusercontent.com/563929/82573621-94be2b00-9bb8-11ea-991c-f7ae5cfffc15.png" align="center" /> 
- Under OAuth & Permissions, scroll down to "Scope" and click "Add an OAuth Scope". This is where you will give your new PAXminer app permissions to do things within your Slack workspace. Add all of the following scopes:
> channels:history, channels:join, channels:read, chat:write, users.profile:read, users:read, users:read.email, commands
- After adding all listed Scope settings, Slack will ask you to "Reinstall App". This just means Slack needs to re-push the app's updated settings. Scroll up and click on "Reinstall App". If the access token changes, make sure to copy it.
- Your Slack environment is now set up for the PAXminer tool to pull messages from your Slack channels.

## Creating an AWS RDS Database

w

## Feedback
- This repository. Submit a PR with your README!

## Contribute

## License

[![CC0](https://licensebuttons.net/p/zero/1.0/88x31.png)](https://creativecommons.org/publicdomain/zero/1.0/)

To the extent possible under law, Scott Schaecher has waived all copyright and related or neighboring rights to this work.
