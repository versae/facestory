from pymongo import MongoClient, ASCENDING

from settings import MONGO_URL


client = MongoClient(MONGO_URL)
database = client.get_default_database()
db = {}
db["faces"] = database.faces
db["users"] = database.users


def get_closest_face_in_painting(symmetry, gender=None):
    """Get the closest face in the dataset by symmetry and return it,
    as well as the painting name, painting age, and painting style"""
    pipeline = []
    if gender:
        pipeline += [{"$match": {"face_gender": gender}}]
    pipeline += [
        {"$project": {
            "id": "$id",
            "painting_url": "$painting_url",
            "painting_age": "$painting_age_number",
            "painting_style": "$painting_style",
            "url": "$face_url",
            "symmetry": "$symmetry",
            "symmetry_diff": {"$subtract": ["$symmetry", symmetry]},
        }},
        {"$project": {
            "id": "$id",
            "painting_url": "$painting_url",
            "painting_age": "$painting_age",
            "painting_style": "$painting_style",
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
    else:
        return None


def save_user_face(face_features):
    """Save a features set of a face in database"""
    db["users"].insert(face_features)
    face_features.pop("_id")


def get_user_faces(image_uuid=None, exclude=None):
    """Retrieve a feature set of a face from database"""
    if exclude is None:
        exclude = []
    exclude += ["_id"]
    user_faces = []
    for user_face in db["users"].find({"image_uuid": image_uuid}):
        for key in exclude:
            if key in user_face:
                user_face.pop(key)
        user_faces.append(user_face)
    return user_faces
