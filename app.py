import os
import re
import logging
from flask import Flask
from slack_sdk.web import WebClient
from slackeventsapi import SlackEventAdapter
from generate_html import generate_html
import json

with open('slack_emoticons_to_html_unicode.json') as json_file:
    slack_emoticons_to_html_unicode = json.load(json_file)

# Initialize a Flask app to host the events adapter
app = Flask(__name__)
# Create an events adapter and register it to an endpoint in the slack app for event injestion.
slack_events_adapter = SlackEventAdapter(os.environ.get("SLACK_EVENTS_TOKEN"), "/slack/events", app)

# Initialize a Web API client
slack_web_client = WebClient(token=os.environ.get("SLACK_TOKEN"))


# When a 'message' event is detected by the events adapter, forward that payload
# to this function.
@slack_events_adapter.on("message")
def message(payload):
    """Parse the message event, and if the activation string is in the text,
    respond with a greeting.
    """

    # Get the event data from the payload
    event = payload.get("event", {})

    # Get the text from the event that came through
    text = event.get("text")

    # Get all mentions in the text by searching for @ followed by a word
    mentions = re.findall("@\w+", text)

    is_bot = False

    for mention in mentions:
        try:
            # Get more information about each mentioned user
            user_info = slack_web_client.users_info(user=mention[1:])
            user_data = user_info.data.get("user")
            # Check if the mentioned user is DharaBot
            is_bot = user_info.status_code == 200 and user_data.get("is_bot") and user_data.get("name") == "coinbot"
        except Exception as e:
            print(e)

    # Check and see if DharaBot was mentioned and the activation phrase was in the text of the message.
    # If so, we respond.
    if is_bot and re.search("save this thread", text.lower()):
        # Since the activation phrase was met, get the channel ID that the event
        # was executed on
        channel_id = event.get("channel")

        if "thread_ts" in event.keys():
            thread_ts = event.get("thread_ts")
            replies = slack_web_client.conversations_replies(channel=channel_id, ts=thread_ts)
            # print(replies.data)

            if replies.status_code == 200 and replies.data['ok']:
                users_info = {}

                custom_emojis = slack_web_client.api_call(
                    api_method='emoji.list'
                )

                for msg in replies.data['messages']:
                    # Get user details if not already fetched
                    if msg['user'] not in users_info.keys():
                        result = slack_web_client.users_info(
                            user=msg['user']
                        )
                        if(result['ok']):
                            users_info[msg['user']] = result['user']

                    userids = set()

                    # Find all occurrences of mentions
                    for mention in re.finditer(r"<@\w*>", msg['text']):
                        # Extract the user id from the mention ie with the starting '<@' and ending '>'
                        userid = msg['text'][mention.start()+2:mention.end()-1]
                        # Get user details if not already fetched
                        if userid not in users_info.keys():
                            result = slack_web_client.users_info(
                                user=userid
                            )
                            if(result['ok']):
                                users_info[userid] = result['user']
                        # Store the user ids in a set for replacing
                        userids.add(userid)

                    for userid in userids:
                        if userid in users_info.keys():
                            # Replace occurences of mentions with user names and appropriate styling
                            msg['text'] = msg['text'].replace('<@'+userid+'>', '<span class="message__mention">@'+users_info[userid]['real_name']+'</span>')

                    emoticons = set()

                    # Find all occurrences of emoticons
                    for emoticoncode in re.finditer(r":\S*:", msg['text']):
                        # Extract the emoticon name from the emoticoncode ie with the starting and ending with ':'
                        emoticon = msg['text'][emoticoncode.start()+1:emoticoncode.end()-1]
                        # Store the emoticons in a set for replacing
                        emoticons.add(emoticon)

                    for emoticon in emoticons:
                        if emoticon in slack_emoticons_to_html_unicode.keys():
                            msg['text'] = msg['text'].replace(':'+emoticon+':', slack_emoticons_to_html_unicode[emoticon])
                        elif custom_emojis['ok'] and emoticon in custom_emojis['emoji']:
                            msg['text'] = msg['text'].replace(':'+emoticon+':', '<img class="message__custom-emoji" src="'+custom_emojis['emoji'][emoticon]+'" />')
                    
                    if 'reactions' in msg.keys():
                        for reaction in msg['reactions']:
                            if reaction['name'] in slack_emoticons_to_html_unicode.keys():
                                reaction['name'] = slack_emoticons_to_html_unicode[reaction['name']]
                            elif custom_emojis['ok'] and reaction['name'] in custom_emojis['emoji']:
                                reaction['name'] = '<img class="message__custom-reaction" src="'+custom_emojis['emoji'][reaction['name']]+'" />'
                
                html_export = generate_html(replies.data['messages'], users_info)
                
                return slack_web_client.files_upload(
                    channels = channel_id,
                    initial_comment = 'Hello there! Thank you for using DharaBot!',
                    file = html_export,
                    title = 'DharaBot thread export',
                    filetype = 'html',
                    thread_ts = thread_ts
                )
            else:
                # Construct the message payload
                message = {
                    "channel": channel_id,
                    "blocks": [
                        {
                            "type": "section", 
                            "text": {
                                "type": "mrkdwn", 
                                "text": "Sorry, something went wrong!"
                            }
                        }
                    ],
                    "thread_ts": thread_ts
                }
        else:
            # Construct the message payload
            message = {
                "channel": channel_id,
                "blocks": [
                    {
                        "type": "section", 
                        "text": {
                            "type": "mrkdwn", 
                            "text": "Sorry, the bot works only in threads :disappointed:"
                        }
                    }
                ],
                "thread_ts": event.get("ts") # Reply in thread of request
            }
        # Send the message payload
        slack_web_client.chat_postMessage(**message)

if __name__ == "__main__":
    # Create the logging object
    logger = logging.getLogger()

    # Set the log level to DEBUG. This will increase verbosity of logging messages
    logger.setLevel(logging.INFO)

    # Add the StreamHandler as a logging handler
    logger.addHandler(logging.StreamHandler())

    app.run(host='0.0.0.0', port=3000)