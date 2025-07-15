from datetime import timedelta
class Config():
    DEBUG = False
    SQLALCHEMY_TRACK_MODIFICATIONS = True

class LocalDevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///vpv2.sqlite3'
    DEBUG = True
    SECRET_KEY = 'secretkey' 
    JWT_SECRET_KEY = 'jwtsecretkey'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)