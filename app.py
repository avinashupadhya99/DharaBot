import os
import re
import logging
from flask import Flask
from slack_sdk.web import WebClient
from slackeventsapi import SlackEventAdapter

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

    # Check and see if the activation phrase was in the text of the message.
    # If so, we respond.
    if re.search("hey dharabot, save this", text.lower()):
        # Since the activation phrase was met, get the channel ID that the event
        # was executed on
        channel_id = event.get("channel")

        if "thread_ts" in event.keys():
            # Construct the message payload
            message = {
                "channel": channel_id,
                "blocks": [
                    {"type": "section", "text": {"type": "mrkdwn", "text": "Hello there! Thank you for using DharaBot!"}}
                ],
                "thread_ts": event.get("thread_ts")
            }
        else:
            # Construct the message payload
            message = {
                "channel": channel_id,
                "blocks": [
                    {"type": "section", "text": {"type": "mrkdwn", "text": "Sorry, the bot works only in threads"}}
                ]
            }
        # Send the message payload
        slack_web_client.chat_postMessage(**message)

if __name__ == "__main__":
    # Create the logging object
    logger = logging.getLogger()

    # Set the log level to DEBUG. This will increase verbosity of logging messages
    logger.setLevel(logging.DEBUG)

    # Add the StreamHandler as a logging handler
    logger.addHandler(logging.StreamHandler())

    app.run(host='0.0.0.0', port=3000)