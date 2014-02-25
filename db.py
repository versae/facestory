import os

from pymongo import MongoClient, ASCENDING

MONGO_URL = os.environ.get('MONGOHQ_URL')
client = MongoClient(MONGO_URL)
database = client.get_default_database()
db = {}
db["faces"] = database.faces


def get_closest_face_in_painting(symmetry, gender=None):
    """Get the closest face in the dataset by symmetry and return it,
    as well as the painting name, painting age, and painting style"""
    pipeline = []
    if gender:
        pipeline += [{"$match": {"face_gender": gender}}]
    pipeline += [
        {"$project": {
            "id": "$id",
            "age": "$painting_age",
            "style": "$painting_style",
            "url": "$face_url",
            "symmetry": "$symmetry",
            "symmetry_diff": {"$subtract": ["$symmetry", symmetry]},
        }},
        {"$project": {
            "id": "$id",
            "age": "$age",
            "style": "$style",
            "url": "$url",
            "symmetry": "$symmetry",
            "diff": {
                "$cond": [{"$lt": ["$symmetry_diff", 0]},
                          {"$multiply": ["$symmetry_diff", -1]},
                          "$symmetry_diff"]
            },
        }},
        {"$sort": {"diff": ASCENDING}},
        {"$limit": 1},
    ]
    documents = db["faces"].aggregate(pipeline)
    if "ok" in documents:
        document = documents["result"][0]
        document.pop("_id")
    return document
