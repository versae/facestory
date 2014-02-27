import math

from boto import connect_s3
from boto.s3.key import Key
import requests

from db import get_closest_face_in_painting
from settings import (SKYBIOMETRY_API_KEY, SKYBIOMETRY_API_SECRET,
                      AWS_STORAGE_BUCKET_NAME)


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
            photo = json["photos"][0]
            photo.pop("pid")
            photo.pop("url")
            return photo
    return None


def get_face_properties(pil_image, face_features):
    """Calculate simmetry of a face and get then information of the painting
    with the closest value"""
    # Point 810 is person mouth_right, 822 mouth_left
    image_width, image_height = pil_image.size
    for point in face_features["points"]:
        if point["id"] == 810:
            face_features["mouth_right"] = point
            if "mouth_left" in face_features:
                break
        if point["id"] == 822:
            face_features["mouth_left"] = point
            if "mouth_right" in face_features:
                break
    features_set = set(face_features.keys())
    if set(["mouth_right", "mouth_left", "mouth_center", "nose",
            "eye_right", "eye_left", "roll", "center"]).issubset(features_set):
        symmetry = get_symmetry(face_features, image_width, image_height)
        gender = None
        if "gender" in face_features["attributes"]:
            gender = face_features["attributes"]["gender"]["value"]
        face = get_closest_face_in_painting(symmetry, gender=gender)
        return {
            'painting_age': face["painting_age"],
            'painting_style': face["painting_style"],
            'symmetry': symmetry,
            'url': face["url"],
        }
    return {
        'painting_age': None,
        'painting_style': None,
        'symmetry': None,
        'url': None,
    }


def point_line_distance(p, a, b):
    """Calcualte the distance between point p (px, py) and
    the line defined as y = ax + b"""
    return abs(a * p[0] - p[1] + b) / math.sqrt(a * a + 1)


def midpoint(p1, p2):
    """Calculate the midpoint between p1 and p2"""
    return ((p1[0] + p2[0]) / 2.0, (p1[1] + p2[1]) / 2.0)


def get_symmetry(face_features, painting_width, painting_height,
                 desired_height=250):
    """Calculate the symmetry of a face"""
    height = 1.0 * painting_height * face_features['height'] / 100
    # width = face_features['width']
    resize_height = (1.0 * painting_height * desired_height / height) / 100.0
    resize_width = (1.0 * painting_width * desired_height / height) / 100.0
    # Hemiline slope and intercept (independent term)
    center = (
        face_features["center"]["x"] * resize_width,
        face_features["center"]["y"] * resize_height
    )
    alpha = face_features["roll"]
    hemiline_m = math.tan(math.radians(90 - alpha))
    hemiline_c = center[1] - hemiline_m * center[0]
    # Midpoints
    eye_left = (
        face_features["eye_left"]["x"] * resize_width,
        face_features["eye_left"]["y"] * resize_height
    )
    eye_right = (
        face_features["eye_right"]["x"] * resize_width,
        face_features["eye_right"]["y"] * resize_height
    )
    m1 = midpoint(eye_left, eye_right)
    mouth_left = (
        face_features["mouth_left"]["x"] * resize_width,
        face_features["mouth_left"]["y"] * resize_height
    )
    mouth_right = (
        face_features["mouth_right"]["x"] * resize_width,
        face_features["mouth_right"]["y"] * resize_height
    )
    m2 = midpoint(mouth_left, mouth_right)
    # Remaining points
    nose = (
        face_features["nose"]["x"] * resize_width,
        face_features["nose"]["y"] * resize_height
    )
    mouth = (
        face_features["mouth_center"]["x"] * resize_width,
        face_features["mouth_center"]["y"] * resize_height
    )
    # Distances
    d1 = point_line_distance(m1, hemiline_m, hemiline_c)
    d2 = point_line_distance(m2, hemiline_m, hemiline_c)
    d3 = point_line_distance(nose, hemiline_m, hemiline_c)
    d4 = point_line_distance(mouth, hemiline_m, hemiline_c)
    return (desired_height - (d1 + d2 + d3 + d4)) / desired_height


def save_file_remote(filename, file_object, headers=None):
    conn = connect_s3()
    bucket = conn.get_bucket(AWS_STORAGE_BUCKET_NAME)
    k = Key(bucket)
    k.key = filename
    num_bytes = k.set_contents_from_string(file_object, headers=headers)
    if not num_bytes:
        return None
    return k.generate_url(expires_in=30)


def get_file_remote(filename, headers=None):
    conn = connect_s3()
    bucket = conn.get_bucket(AWS_STORAGE_BUCKET_NAME)
    k = bucket.get_key(filename, headers=headers)
    if not k:
        return None
    return k.generate_url(expires_in=30)
