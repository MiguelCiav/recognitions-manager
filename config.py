import os
from dotenv import load_dotenv

load_dotenv()
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    DEBUG = True
    UPLOAD_FOLDER = os.path.join(basedir, 'output')
    DATABASE_PATH = os.path.join(basedir, 'data', 'reconocimientos.db')
    SCOUT_USERNAME = os.environ.get('SCOUT_USERNAME')
    SCOUT_PASSWORD = os.environ.get('SCOUT_PASSWORD')