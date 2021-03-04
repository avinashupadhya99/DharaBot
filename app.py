import os
import re
import logging
from flask import Flask
from slack_sdk.web import WebClient
from slackeventsapi import SlackEventAdapter
from generate_html import generate_html

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
                for message in replies.data['messages']:
                    print(message["text"])

                print(generate_html(replies.data['messages']))

                # Construct the message payload
                message = {
                    "channel": channel_id,
                    "blocks": [
                        {
                            "type": "section", 
                            "text": {
                                "type": "mrkdwn", 
                                "text": "Hello there! Thank you for using DharaBot!"
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