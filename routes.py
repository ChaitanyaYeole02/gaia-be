import os
import json
import tempfile

import google.generativeai as genai
import requests

from flask import Blueprint, jsonify, request
from dotenv import load_dotenv

from db import db

load_dotenv()
test = Blueprint('test', __name__)
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

UPLOAD_FOLDER = "/"


@test.route('/')
def index():
    return "Server Working"


@test.route('/get_markers', methods=['GET'])
def get_markers():
    try:
        markers = []

        for marker in db.markers.find():
            markers.append({
                'id': marker['_id'],
                'title': marker['description'],
                'position': {
                    'lat': marker['location']['coordinates'][1],
                    'lng': marker['location']['coordinates'][0]
                }
            })

        return markers
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500


@test.route('/get_marker_info', methods=['GET'])
def get_marker_info():
    try:
        marker_id = request.args.get('marker_id')
        info = {}

        description = db.markers.find_one({'_id': marker_id}).get('description')
        info['description'] = description

        pipeline = [
            {
                '$match': {
                    'marker_id': marker_id,
                    'status': 'completed'
                }
            },
            {
                '$lookup': {
                    'from': 'tasks',
                    'localField': 'task_id',
                    'foreignField': 'id',
                    'as': 'task_details'
                }
            },
            {
                '$unwind': '$task_details'
            },
            {
                '$project': {
                    '_id': 0,
                    'task_id': 1,
                    'task_name': '$task_details.taskName'
                }
            }
        ]

        completed_tasks_cursor = db.user_tasks.aggregate(pipeline)
        completed_tasks = list(completed_tasks_cursor)
        completed_task_ids = [task['task_id'] for task in completed_tasks]

        incomplete_tasks_cursor = db.tasks.find({'id': {'$nin': completed_task_ids}})
        incomplete_tasks = list(incomplete_tasks_cursor)

        info['completed_tasks'] = [{'task_id': task['task_id'], 'task_name': task['task_name']} for task in
                                   completed_tasks]
        info['incompleted_tasks'] = [{'task_id': task['id'], 'task_name': task['taskName']} for task in
                                     incomplete_tasks]
        print(info)

        return info

    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500


@test.route('/get_difference', methods=['POST'])
def get_difference():
    try:
        before_image = request.files['before_image']
        after_image = request.files['after_image']

        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(before_image.filename)[1],
                                         dir=UPLOAD_FOLDER) as temp_before:
            before_image.save(temp_before.name)
            before_image_path = temp_before.name

        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(after_image.filename)[1],
                                         dir=UPLOAD_FOLDER) as temp_before:
            after_image.save(temp_before.name)
            after_image_path = temp_before.name

        model = genai.GenerativeModel("gemini-1.5-flash")
        before_image = genai.upload_file(path=before_image_path)
        after_image = genai.upload_file(path=after_image_path)

        response = model.generate_content([
            before_image,
            after_image, "\n\n",
            "Compare these two images then check their differences and tell me if the person has done anything "
            "good for the environment. \n "
            "If yes or no then provide me an answer yes or no and a small description of what the person did. \n"
            "Provide me the final answer in a dictionary format like {'answer': 'Yes', 'description': ''}"
        ])

        os.unlink(before_image_path)
        os.unlink(after_image_path)

        return jsonify(response.text), 200
    except Exception as e:
        print(f"An exception occurred: {e}")
        return jsonify({"error": str(e)}), 500


@test.route('/add_task', methods=['POST'])
def add_task():
    try:
        before_image = request.files['beforeImage']
        after_image = request.files['afterImage']
        description = request.values['description']
        marker_id = request.values['markerId']
        task_id = request.values['taskId']

        return {}
    except Exception as e:
        print(f"An exception occurred: {e}")
        return jsonify({"error": str(e)}), 500
 