import ast
import os
import tempfile

import google.generativeai as genai

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

        return info

    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500


@test.route('/get_user_tasks', methods=['GET'])
def get_user_tasks():
    try:
        user_id = request.args.get('user_id')

        pipeline = [
            {
                '$match': {
                    'user_id': user_id
                }
            },
            {
                '$lookup': {
                    'from': 'markers',
                    'localField': 'marker_id',
                    'foreignField': '_id',
                    'as': 'marker_info'
                }
            },
            {
                '$unwind': {
                    'path': '$marker_info',
                    'preserveNullAndEmptyArrays': True
                }
            },
            {
                '$lookup': {
                    'from': 'tasks',
                    'localField': 'task_id',
                    'foreignField': 'id',
                    'as': 'task_info'
                }
            },
            {
                '$unwind': {
                    'path': '$task_info',
                    'preserveNullAndEmptyArrays': True
                }
            },
            {
                '$project': {
                    '_id': 0,
                    'description': 1,
                    'location': '$marker_info.description',
                    'task_name': '$task_info.taskName',
                    'points': 1
                }
            }
        ]

        user_tasks_cursor = db.user_tasks.aggregate(pipeline)
        user_tasks = list(user_tasks_cursor)

        return user_tasks
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
        user_id = request.values['userId']

        answer, gemini_description = get_images_difference(before_image, after_image, description)

        if answer == 'No':
            return jsonify({
                "answer": answer,
                "description": gemini_description
            })
        else:
            doc = {
                'marker_id': marker_id,
                'task_id': task_id,
                'user_id': user_id,
                'description': description,
                'status': 'completed',
                'points': 10
            }
            db.user_tasks.insert_one(doc)

            return jsonify({
                "answer": answer,
                "description": gemini_description
            })
    except Exception as e:
        print(f"An exception occurred: {e}")
        return jsonify({"error": str(e)}), 500


def get_images_difference(before_image, after_image, description):
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
        after_image,
        description,
        "\n\n",
        "Compare these two images then check their differences and tell me if the person has done anything "
        "good for the environment. Also check if the description provided matches with the image. \n "
        "If yes or no then provide me an answer yes or no and a small description of what the person did. \n"
        "Provide me the final answer in a dictionary format like {'answer': 'Yes', 'description': ''}"
    ])

    os.unlink(before_image_path)
    os.unlink(after_image_path)

    decoded_str = jsonify(response.text)
    decoded_str = decoded_str.response[0].decode('utf-8')
    cleaned_str = decoded_str.strip().strip('"').strip()
    if cleaned_str.endswith('\\n'):
        cleaned_str = cleaned_str[:-2].strip()
    result = ast.literal_eval(cleaned_str)

    return result['answer'], result['description']
 