import os

from gridfs import GridFS
from pymongo import MongoClient

MONGO_URL = os.environ.get('MONGOHQ_URL')
client = MongoClient(MONGO_URL)
db = client.data
files = GridFS(db)
faces = db.faces
