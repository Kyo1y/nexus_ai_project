import logging
from application import create_app
from flask_cors import CORS


if __name__ == '__main__':
    app = create_app()
    cors = CORS(app)
    app.config['CORS_HEADERS'] = 'Content-Type'
    app.run(port=5000, debug=False)
