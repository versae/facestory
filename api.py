# -*- coding: utf-8 -*-
import cStringIO
import os
import re
import uuid

import requests

from flask import request
from flask.ext import restful
from flask.ext.restful import reqparse

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
SKYBIOMETRY_API_KEY = os.environ['SKYBIOMETRY_API_KEY']
SKYBIOMETRY_API_SECRET = os.environ['SKYBIOMETRY_API_SECRET']


class FaceSimilarity(restful.Resource):

    def get(self):
        return {'hello': 'world'}

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('data_uri', type=str, required=True,
                            help='Data URI with the image of a face')
        args = parser.parse_args()
        # Get image from request
        data_uri = args['data_uri']
        image_id = uuid.uuid4().hex
        image_name = u"{}.png".format(image_id)
        image_path = os.path.join(PROJECT_ROOT, "static", "faces", image_name)
        image_url = u"/static/faces/{}".format(image_name)
        image_str = re.search(r'base64,(.*)', data_uri).group(1)
        image_base64 = image_str.decode('base64')
        # Save image in disk
        message = u"OK"
        try:
            output = open(image_path, 'wb')
            output.write(image_base64)
            output.close()
        except IOError:
            message = u"Error when saving image in disk"
        # Create image in memory
        image_tmp = cStringIO.StringIO(image_base64)
        image_faces = get_image_faces(image_tmp)
        #im = Image.open(image_tmp)
        return {
            'image_url': image_url,
            'host': request.host,
            'message': message,
            'faces': image_faces,
        }


def add_api(app):
    api = restful.Api(app)
    api.add_resource(FaceSimilarity, '/api/similarity')


def get_image_faces(file_obj):
    url = u"http://api.skybiometry.com/fc/faces/detect.json"
    data = {
        "api_key": SKYBIOMETRY_API_KEY,
        "api_secret": SKYBIOMETRY_API_SECRET,
        "urls": "",
        "attributes": "all",
        "detect_all_feature_points": "true",
    }
    files = {'file': file_obj}
    response = requests.post(url, data=data, files=files)
    json = {}
    if response.status_code == requests.codes.ok:
        json = response.json()
        if json["status"] == u"success":
            return json["photos"][0]
    return None
