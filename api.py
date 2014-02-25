# -*- coding: utf-8 -*-
import io
import os
import re
import uuid

from PIL import Image

from flask import request
from flask.ext import restful
from flask.ext.restful import reqparse

from db import save_user_face
from utils import get_face_properties, get_image_faces, save_file_remote
from settings import PROJECT_ROOT


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
        image_str = re.search(r'base64,(.*)', data_uri).group(1)
        image_base64 = image_str.decode('base64')
        # Save image in disk
        message = u"OK"
        error = u""
        image_url = save_file_remote(image_name, image_base64,
                                     headers={"Content-Type": "image/png"})
        if not image_url:
            image_url = u"/static/faces/{}".format(image_name)
            try:
                output = open(image_path, 'wb')
                output.write(image_base64)
                output.close()
            except IOError:
                error = u"Error when saving image in disk"
        # Create image in memory
        image = Image.open(io.BytesIO(image_base64))
        image_faces = get_image_faces(io.BytesIO(image_base64))
        ages = []
        styles = []
        data_uris = []
        symmetries = []
        if not image_faces or len(image_faces['tags']) == 0:
            message = u"No faces found"
        else:
            for image_face in image_faces['tags']:
                face_properties = get_face_properties(image, image_face)
                ages.append(face_properties["age"])
                styles.append(face_properties["style"])
                data_uris.append(face_properties["data_uri"])
                symmetries.append(face_properties["symmetry"])
                # Saving the info to the database
                image_face["uuid"] = image_id
                image_face["similarity_age"] = face_properties["age"]
                image_face["similarity_style"] = face_properties["style"]
                image_face["similarity_face_url"] = face_properties["data_uri"]
                save_user_face(image_face)
                image_face.pop("_id")  # added by pymongo
        return {
            'image_url': image_url,
            'host': request.host,
            'message': message,
            'error': error,
            'faces': image_faces,
            'ages': ages,
            'styles': styles,
            'data_uris': data_uris,
            'symmetries': symmetries,
        }


def add_api(app):
    api = restful.Api(app)
    api.add_resource(FaceSimilarity, '/api/similarity')
