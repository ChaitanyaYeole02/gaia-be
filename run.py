import os 
import configparser
from flask import Flask 
# from .db import init_db  
from routes import test

def create_app():
    app = Flask(__name__)
    config = configparser.ConfigParser()
    config.read(os.path.abspath(os.path.join('config.ini')))

    # Configure Flask MongoDB URI
    app.config['MONGO_URI'] = "mongodb+srv://quynhho1601:dXWBa84LToNdQs8q@cluster0.rt183.mongodb.net/"

    # Initialize additional configurations or extensions here
    with app.app_context():
        app.register_blueprint(test)                                                                                        
    return app




#write a get api and fetch markers data from mongodb
app = create_app()

if __name__ == "__main__":
    app.run(debug=True)

