import os

UPLOAD_FOLDER = 'static/uploads'
GCP_BUCKET = os.environ.get('GCP_BUCKET', '')
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_PORT = os.environ.get('DB_PORT', '5432')
DB_USER = os.environ.get('DB_USER', '')
DB_PASS = os.environ.get('DB_PASS', '')
DB_DB = os.environ.get('DB_DB', '')

SQLALCHEMY_DATABASE_URI = f'postgresql://{DB_HOST}:{DB_PORT}/{DB_DB}?user={DB_USER}&password={DB_PASS}'
