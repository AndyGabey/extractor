import os

from flask import Flask
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect

login_manager = LoginManager()
# Create flask object and configure based on site specific host_config.txt
app = Flask(__name__)
config = open(os.path.join(app.root_path, 'host_config.txt'), 'r').read().strip()
app.config.from_object(config)
app.secret_key = 'secret123changethis_to_something_a_bit_h@rd3r_2_guest??'

login_manager.init_app(app)
csrf = CSRFProtect(app)

login_manager.login_view = "login"

import Extractor.views
from Extractor.database import db_session


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


if __name__ == '__main__':
    app.run(debug=True, use_debugger=False, use_reloader=False)
