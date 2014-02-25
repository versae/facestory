
import os

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

MONGO_URL = os.environ.get('MONGOHQ_URL')

SKYBIOMETRY_API_KEY = os.environ['SKYBIOMETRY_API_KEY']
SKYBIOMETRY_API_SECRET = os.environ['SKYBIOMETRY_API_SECRET']

AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']
AWS_STORAGE_BUCKET_NAME = os.environ['AWS_STORAGE_BUCKET_NAME']
