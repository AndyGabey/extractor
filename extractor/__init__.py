import os

from flask import Flask

# Create flask object and configure based on site specific host_config.txt
app = Flask(__name__)
dir_path = os.path.dirname(os.path.realpath(__file__))
config = open(os.path.join(dir_path, 'host_config.txt'), 'r').read().strip()
app.config.from_object(config)


import extractor.views

if __name__ == '__main__':
    app.run()
