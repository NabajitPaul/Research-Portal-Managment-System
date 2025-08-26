import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-very-secret-key' # Change this!
    #SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://username:password@host/dbname' # e.g., 'mysql+mysqlconnector://user:pass@localhost/research_db'
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://root:mysql@localhost/research_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = 'uploads' # Relative to the app.py location
    ORCID_API_BASE_URL = 'https://pub.orcid.org/v3.0/'