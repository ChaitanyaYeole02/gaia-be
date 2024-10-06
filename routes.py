import os
import json

import google.generativeai as genai

from flask import Blueprint, jsonify, request
from dotenv import load_dotenv

from db import db

load_dotenv()
test = Blueprint('test', __name__)

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


@test.route('/')
def index():
    return "Server Working"


@test.route('/get_markers', methods=['GET'])
def get_markers():
    markers_dict = {}
    for element in db.markers.find():
        markers_dict[element['_id']] = element
    return markers_dict


@test.route('/get_difference', methods=['POST'])
def get_difference():
    try:
        after_image = request.files['after_image']
        model = genai.GenerativeModel("gemini-1.5-flash")
        before_image = genai.upload_file(request.files['before_image'])
        after_image = genai.upload_file(path="test_image.jpg")
        print(before_image, after_image)

        # response = model.generate_content(
        #     [before_image, after_image, "\n\n", "Compare these two images and highlight their differences."]
        # )

        # return response.text
        return {}

    except Exception as e:
        print(f"An exception occurred: {e}")
        return jsonify({"error": str(e)}), 500
 