from jinja2 import Environment, FileSystemLoader
import os
import uuid
import datetime

def generate_html(data, users_info):
    # print(users_info)
    # print(data)
    root = os.path.dirname(os.path.abspath(__file__))
    templates_dir = os.path.join(root, 'templates')
    env = Environment( loader = FileSystemLoader(templates_dir) )
    template = env.get_template('index.html')

    fileuuid = uuid.uuid1()

    filename = os.path.join(root, 'html', f'{fileuuid}.html')
    with open(filename, 'w') as fh:
        fh.write(template.render(
            messages = data,
            users_info = users_info,
            datetime = datetime
        ))

        return './html/'+str(fileuuid)+'.html'