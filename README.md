# SLACK LOGBOOK
The goal is to log your work in a spreadsheet using a [slash command of slack](https://api.slack.com/slash-commands). For example, we use `/ambrogio  my work | 8` where

- `ambrogio` is the name of the command (from a famous ads from Italy. )
- `my work` is what you write as entry to be logged in a spreadsheet
- `|` delimiter (I haven't found an easier way for this)
- `8` a vote on your productivity. It's useful to have a quick look at your day later on.

This command will add a row in a spreadsheet on google docs with the date of yesterda, the message and the vote.

Every day it sends a reminder to the people listed in the configuration. (TODO: this should be avoided during weekend). Everyday, if the log of yesterday is missed, it adds one automatically, just to fill in everyday of the year.

##NOTE

**This version is for a self hosted solution**, you have to setup everything by yourself. It's probably not the easiest thing to provide. However, you are the owner of everything.

In the future I plan to provide a slack app that can be easily integrate. But who knows how long it will take.

## Install
This code is made for Google App Engine (GAE). I chose GAE beacuse:

- It's free for such small projects
- It's easy to integrate google products (guess why)
- It's built in cron and recursive tasks
- It's easy to create small apps and endpoints
- (It also scale well, but this is not the case)

### Procedure

- Create a GAE app [here](https://console.cloud.google.com/appengine)
- install library `pip install --upgrade  -t lib/ google-api-python-client` and `pip install --upgrade -t lib/ httplib2`
- Set in the `app.yaml` file your application name `application: <HERE>`.
- Enable API for spreadsheet (in the API page)
- In the AMI - Credentials, note down the email of the system, it should be `..appname@developer.appspot..` or something like that
- Create a spreadsheet in your GDrive, and share with the email that you noted from previous step.
- Add as the first row `DATE, MESSAGE, VOTE` as 3 columns. And as second row `2016-01-01, Dummy, 0` in the three columns. (this is needed for the initialization)
- Copy the SpreedsheetId from the url (something like a code, eg `15I7Ipbt........fEissA`) and set it in the configuration file (`cfg.py` - see Configuration paragraph).
- Go to slack and enable a command a `slash command` https://my.slack.com/services/new/slash-commands

    - name: whatever you want to call it, we use `ambrogio`
    - url: your GAE url, smt like `https://slack-logbook....appspot.com/`
    - method: `POST`
    - token: whatever is there, *COPY IT*
    - for the rest personalize it as you like it.

- Put the copied token and write it in the config of the project (`cfg.py` - see Configuration paragraph).
- Write the username of slack in the config (`cfg.py` - see Configuration paragraph). These are the people who can write in the logbook.
- Add a spreedsheet page for each user. Naming the paper as the nickname (in my case is `stefano`)
- Deploy the app `appcfg.py update .` in the folder of the projects

### Configuration

 - SHEET_ID: the spreadsheet id from the url
 - TOKEN: slack slash command token, to auth the calls
 - INCOMING_WH: a valid slash incoming webhook, to send notifications. [create here](https://my.slack.com/services/new/incoming-webhook/), copy the link (or you can use an existing one).
 - USERS: list of users by their usernames. NOTE: you must have a spreadsheet page for each user named with their name.
 - ICON: the icon of the bot.
 - USERNAME: the username that will be displayed

#### Local Development

- Create the credentials for the project from the google console and put it in `~/.config/gcloud/defualt-credentials.json`
