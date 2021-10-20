import os


DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PORT = os.environ.get("DB_PORT", "5432")
DB_USER = os.environ.get("DB_USER", "")
DB_PASS = os.environ.get("DB_PASS", "")
DB_NAME = os.environ.get("DB_NAME", "")

SQLALCHEMY_DATABASE_URI = (
    f"postgresql://{DB_HOST}:{DB_PORT}/{DB_NAME}?user={DB_USER}&password={DB_PASS}"
)

GCP_BUCKET = os.environ.get("GCP_BUCKET", "")
