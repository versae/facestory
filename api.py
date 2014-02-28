# -*- coding: utf-8 -*-
import io
import os
import re
import uuid

from PIL import Image

from flask import request
from flask.ext import restful
from flask.ext.restful import reqparse

from db import save_user_face, get_user_face
from utils import (get_face_properties, get_image_faces,
                   save_file_remote, get_file_remote)
from settings import PROJECT_ROOT


class FaceSimilarity(restful.Resource):

    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('photo_id', type=str, required=True,
                            help='Photo UUID to retrieve')
        parser.add_argument('include_data_uri', type=bool, required=False,
                            default=True, help='Photo UUID to retrieve')
        args = parser.parse_args()
        photo_id = args["photo_id"]
        include_data_uri = args["include_data_uri"]
        if photo_id:
            faces = get_user_face(photo_id)
            photo_filename = "{}.png".format(photo_id)
            image_data_uri = get_file_remote(photo_filename,
                                             data_uri=include_data_uri)
            if faces:
                return {
                    "faces": faces,
                    "message": "OK",
                    "image_data_uri": image_data_uri,
                    "image_id": photo_id,
                }
        return {
            "faces": [],
            "message": "Invalid photo id",
            "image_data_uri": "",
            "image_id": ""
        }

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
        urls = []
        symmetries = []
        if not image_faces or len(image_faces['tags']) == 0:
            message = u"No faces found"
        else:
            for image_face in image_faces['tags']:
                face_props = get_face_properties(image, image_face)
                ages.append(face_props["painting_age"])
                styles.append(face_props["painting_style"])
                urls.append(face_props["url"])
                symmetries.append(face_props["symmetry"])
                # Saving the info to the database
                image_width, image_height = image.size
                image_face["image_uuid"] = image_id
                image_face["image_url"] = image_url
                image_face["image_filename"] = image_name
                image_face["image_width"] = image_width
                image_face["image_height"] = image_height
                image_face["painting_age"] = face_props["painting_age"]
                image_face["painting_style"] = face_props["painting_style"]
                image_face["face_id"] = face_props["id"]
                image_face["face_url"] = face_props["url"]
                image_face["face_symmetry"] = face_props["symmetry"]
                save_user_face(image_face)
                image_face.pop("_id")  # added by pymongo
        return {
            'image_url': image_url,
            'image_id': image_id,
            'host': request.host,
            'message': message,
            'error': error,
            'faces': image_faces.get("tags", []),
            'ages': ages,
            'styles': styles,
            'urls': urls,
            'symmetries': symmetries,
        }


def add_api(app):
    api = restful.Api(app)
    api.add_resource(FaceSimilarity, '/api/similarity')
