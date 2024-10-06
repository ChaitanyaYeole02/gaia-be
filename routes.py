from flask import Blueprint
from flask.json import jsonify
from flask_pymongo import PyMongo
from db import db  # Import the global `db` object

test = Blueprint('test', __name__)

@test.route('/')
def index():
    return "Server Working"


@test.route('/get_markers', methods=['GET'])
def get_markers():
    markers_dict = {}
    for element in db.markers.find():
        markers_dict[element['_id']] = element
    return markers_dict

 