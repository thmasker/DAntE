from os import environ, path
from dotenv import load_dotenv
from datetime import timedelta

basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, '.env'))


class Config:
    SERVER_NAME = 'localhost:2000'
    SECRET_KEY = environ.get('SECRET_KEY')
    SESSION_COOKIE_NAME = environ.get('SESSION_COOKIE_NAME')
    STATIC_FOLDER = 'static'
    TEMPLATES_FOLDER = 'templates'
    MAX_CONTENT_LENGTH = 500 * 1024 * 1024
    MONGO_DBNAME = 'dante'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=3)
    DATA_DIR = 'data'


class ProdConfig(Config):
    FLASK_ENV = 'production'
    DEBUG = False
    TESTING = False
    MONGO_URI = environ.get('PROD_DATABASE_URI')

class DevConfig(Config):
    FLASK_ENV = 'development'
    DEBUG = True
    TESTING = True
    MONGO_URI = environ.get('DEV_DATABASE_URI')