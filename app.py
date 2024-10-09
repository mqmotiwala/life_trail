from flask import Flask
from logger import logger
from routes import configure_routes

app = Flask(__name__)
configure_routes(app)

if __name__ == '__main__':
    logger.info("Starting Flask server...")
    app.run(host='0.0.0.0', port=5000, debug=True)