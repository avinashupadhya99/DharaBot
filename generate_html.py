from jinja2 import Environment, FileSystemLoader
import os
import uuid

def generate_html(data):
    root = os.path.dirname(os.path.abspath(__file__))
    templates_dir = os.path.join(root, 'templates')
    env = Environment( loader = FileSystemLoader(templates_dir) )
    template = env.get_template('index.html')

    fileuuid = uuid.uuid1()
    
    filename = os.path.join(root, 'html', f'{fileuuid}.html')
    with open(filename, 'w') as fh:
        fh.write(template.render(
            h1 = "Hello Jinja2",
            show_one = True,
            show_two = False,
            names    = ["Foo", "Bar", "Qux"],
        ))

        return fileuuid