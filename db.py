from flask import g
from flask_pymongo import PyMongo
from werkzeug.local import LocalProxy

# Initialize PyMongo
mongo = PyMongo()

def init_db(app):
    """
    Initialize the database and set up the app configuration.
    """
    mongo.init_app(app)  # Link PyMongo to the Flask app

def get_db():
    """
    Get the current database connection.
    If it doesn't exist, establish a new one in `g`.
    """
    if 'db' not in g:
        g.db = mongo.db  # Access the MongoDB database object
    return g.db

# Use LocalProxy to access the global db instance as `db`
db = LocalProxy(get_db)
