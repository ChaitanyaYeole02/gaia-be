import os 
import configparser

from flask import Flask
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


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
