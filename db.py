import os

from gridfs import GridFS
from pymongo import MongoClient, ASCENDING

MONGO_URL = os.environ.get('MONGOHQ_URL')
client = MongoClient(MONGO_URL)
database = client.get_default_database()
db = {}
db["files"] = GridFS(database)
db["faces"] = database.faces


def get_closest_face_in_painting(symmetry):
    """Get the closest face in the dataset by symmetry and return it,
    as well as the painting name, painting age, and painting style"""
    documents = db["faces"].aggregate([
        {"$project": {
            "id": "$id",
            "age": "$painting_age_number",
            "style": "$painting_style",
            "symmetry": "$symmetry",
            "symmetry_diff": {"$subtract": ["$symmetry", symmetry]},
        }},
        {"$project": {
            "id": "$id",
            "age": "$age",
            "style": "$style",
            "symmetry": "$symmetry",
            "diff": {
                "$cond": [{"$lt": ["$symmetry_diff", 0]},
                          {"$multiply": ["$symmetry_diff", -1]},
                          "$symmetry_diff"]
            },
        }},
        {"$sort": {"diff": ASCENDING}},
        {"$limit": 1},
    ])
    if "ok" in documents:
        document = documents["result"][0]
        document.pop("_id")
        document["data_uri"] = None
        if db["files"].exists({"filename": document["id"]}):
            image = db["files"].get_last_version(document["id"])
            document["data_uri"] = image.read()
    return document
