from flask import Flask
import os
from logger import logger
from routes import configure_routes
from logger import setup_logger, logger

app = Flask(__name__)

# Set a secret key for session management
app.secret_key = os.urandom(24)

# get reference to root folder for absolute path of project files
root = os.path.dirname(__file__)
setup_logger(root)

configure_routes(app)

if __name__ == '__main__':
    logger.info("Starting Flask server...")
    app.run(host='0.0.0.0', port=5000, debug=True)