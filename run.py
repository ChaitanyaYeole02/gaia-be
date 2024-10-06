import os 
import configparser

from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv

from db import init_db
from routes import test


def create_app():
    app = Flask(__name__)
    load_dotenv()
    app.config['MONGO_URI'] = os.getenv('MONGO_URI')

    with app.app_context():
        app.register_blueprint(test)

    init_db(app)

    return app


app = create_app()
CORS(app, resources={r"/get_markers": {"origins": "http://localhost:3000"}})
CORS(app, resources={r"/get_marker_info": {"origins": "http://localhost:3000"}})
CORS(app, resources={r"/add_task": {"origins": "http://localhost:3000"}})

if __name__ == "__main__":
    app.run(debug=True, port=8000)
