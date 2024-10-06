from flask import g
from flask_pymongo import PyMongo
from werkzeug.local import LocalProxy

mongo = PyMongo()


def init_db(app):
    """
    Initialize the database and set up the app configuration.
    """
    mongo.init_app(app)


def get_db():
    """
    Get the current database connection.
    If it doesn't exist, establish a new one in `g`.
    """
    if 'db' not in g:
        g.db = mongo.db

    return g.db


db = LocalProxy(get_db)
