import os

import requests

SKYBIOMETRY_API_KEY = os.environ['SKYBIOMETRY_API_KEY']
SKYBIOMETRY_API_SECRET = os.environ['SKYBIOMETRY_API_SECRET']


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
        if json["status"] == u"success" and len(json["photos"]) > 0:
            return json["photos"][0]
    return None


def get_face_properties(image, image_face):
    # Point 810 is person mouth_right, 822 mouth_left
    return {
        'age': None,
        'style': None,
        'data_uri': None,
    }
