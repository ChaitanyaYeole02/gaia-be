from flask import Blueprint, jsonify
from db import db  # Import the global `db` object

test = Blueprint('test', __name__)

@test.route('/')
def index():
    return "Server Working"


@test.route('/get_markers', methods=['GET'])
def get_markers():
    # Get the data from mongo
    # jsonify and return it back
    return "fetched"

 