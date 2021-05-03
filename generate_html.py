from jinja2 import Environment, FileSystemLoader
import os
import uuid
import datetime
import re

def generate_html(data, users_info):
    # print(users_info)
    # print(data)
    root = os.path.dirname(os.path.abspath(__file__))
    templates_dir = os.path.join(root, 'templates')
    env = Environment( loader = FileSystemLoader(templates_dir) )
    template = env.get_template('index.html')

    fileuuid = uuid.uuid1()

    for message in data:
        # Find all occurrences of mentions
        for mention in re.finditer(r"^<@\w*>", message['text']):
            # Extract the user id from the mention ie with the starting '<@' and ending '>'
            userid = message['text'][mention.start()+2:mention.end()-1]
            # Replace occurences of mentions with user names and appropriate styling
            message['text'] = message['text'].replace('<@'+userid+'>', '<span class="message__mention">@'+users_info[userid]['real_name']+'</span>')

    filename = os.path.join(root, 'html', f'{fileuuid}.html')
    with open(filename, 'w') as fh:
        fh.write(template.render(
            messages = data,
            users_info = users_info,
            datetime = datetime
        ))

        return fileuuid