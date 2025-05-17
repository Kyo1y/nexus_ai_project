import logging.config
import os

import yaml

from flask import Flask

def create_app():
    app = Flask(__name__)
    # app.config.from_object(config_class)
    app.secret_key = 'f788cd11f1ce8a3d81cb183c7750e4fbbe09d8dcffb19b90b05488a8cf622f91'
    # Initialize Flask extensions here

    # Register blueprints here
    from application.chat import chat_bp
    from application.viewer import viewer_bp
    app.register_blueprint(chat_bp, url_prefix='/chat')
    app.register_blueprint(viewer_bp, url_prefix='/viewer')

    curr_dir = os.path.dirname(__file__)
    with open(os.path.join(curr_dir, 'configs/logging.yaml'), 'r') as yaml_file:
        logging_config = yaml.load(yaml_file, yaml.SafeLoader)
    logging.config.dictConfig(logging_config)

    @app.route('/test/')
    def test_page():
        return '<h1>Testing the Flask Application Factory Pattern</h1>'

    return app
