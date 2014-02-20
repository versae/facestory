import os
import math

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


def point_line_distance(p, a, b):
    """Calcualte the distance between point p (px, py) and
    the line defined as y = ax + b"""
    return abs(a * p[0] - p[1] + b) / math.sqrt(a * a + 1)


def midpoint(p1, p2):
    """Calculate the midpoint between p1 and p2"""
    return ((p1[0] + p2[0]) / 2.0, (p1[1] + p2[1]) / 2.0)


def get_symmetry(face_features, desired_height=250):
    """Calculate the symmetry of a face"""
    height = face_features['height']
    width = face_features['width']
    painting_height = face_features['painting_height']
    painting_width = face_features['painting_width']
    resize_height = (1.0 * painting_height * desired_height / height) / 100.0
    resize_width = (1.0 * painting_width * desired_height / height) / 100.0
    # Hemiline slope and independent term
    center = (
        face_features["center_x_pct"] * resize_width,
        face_features["center_y_pct"] * resize_height
    )
    alpha = face_features["roll"]
    hemiline_m = math.tan(alpha)
    hemiline_c = center[1] - hemiline_m * center[0]
    # Midpoints
    eye_left = (
        face_features["eye_left_x_pct"] * resize_width,
        face_features["eye_left_y_pct"] * resize_height
    )
    eye_right = (
        face_features["eye_right_x_pct"] * resize_width,
        face_features["eye_right_y_pct"] * resize_height
    )
    m1 = midpoint(eye_left, eye_right)
    mouth_left = (
        face_features["mouth_left_x_pct"] * resize_width,
        face_features["mouth_left_y_pct"] * resize_height
    )
    mouth_right = (
        face_features["mouth_right_x_pct"] * resize_width,
        face_features["mouth_right_y_pct"] * resize_height
    )
    m2 = midpoint(mouth_left, mouth_right)
    # Remaining points
    nose = (
        face_features["nose_x_pct"] * resize_width,
        face_features["nose_y_pct"] * resize_height
    )
    mouth = (
        face_features["mouth_center_x_pct"] * resize_width,
        face_features["mouth_center_y_pct"] * resize_height
    )
    # Distances
    d1 = point_line_distance(m1, hemiline_m, hemiline_c)
    d2 = point_line_distance(m2, hemiline_m, hemiline_c)
    d3 = point_line_distance(nose, hemiline_m, hemiline_c)
    d4 = point_line_distance(mouth, hemiline_m, hemiline_c)
    return (desired_height - (d1 + d2 + d3 + d4)) / desired_height
