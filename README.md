# DharaBot

A Slack Bot to save threads as HTML.

### Developer Documentation

Steps to run the bot on your workspace/locally (Note that you will need a publically available port, use a VPS VM if available)

1. Create a new Workspace or log onto your existing Workspace in a browser and go to the [Slack API Control Panel](https://api.slack.com/apps). Click on **Create New App**.
2. Name it as *DharaBot* and click on Create App.
3. Go to **OAuth & Permission** > Under **Scopes**, **Bot Token Scopes** > **Add an OAuth Scope** > *chat:write*, *emoji:read*, *files:write* and *users:read*
4. Go to **Event Subscriptions** and toggle ON the **Enable Events** and add the *Request URL* as `http://<YOUR_PUBLIC_IP>:3000/slack/events` and click on **Save Changes**.
5. Install the bot into Workspace by clicking on **Install to Workspace** in the same page > **Allow**. Copy the *Bot User OAuth Access Token* for further use as SLACK_TOKEN.
6. Open your Workspace and add the app to any channel.
7. Run the following commands on your terminal to set up the application on your local (Make sure you have Python3) - 
- `git clone https://github.com/avinashupadhya99/DharaBot.git` or fork it and use ssh.
- `cd DharaBot`
- `mkdir ~/.venvs` (Create directory for virtual environments)
- `python3 -m venv ~/.venvs/dharabot` (Create virtual environment)
- `source ~/.venvs/dharabot/bin/activate` (Activate environment) (You should see `(dharabot)` at the start of your terminal line)
- `pip install -r requirements.txt`
- `export SLACK_TOKEN=<YOUR_BOT_USER_OAUTH_ACCESS_TOKEN>`
- `export SLACK_EVENTS_TOKEN="YOUR_SIGNING_SECRET_TOKEN"` (You can find this under **Basic Information**, under **App Credentials** as *Signing Secret* in the control panel.
- `python app.py` (This should start the application on all hosts at port 3000)
8. Refer to [Bot Usage]() for testing the bot.
