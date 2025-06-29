class Config():
    DEBUG = False
    SQLALCHEMY_TRACK_MODIFICATIONS = True

class LocalDevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///vpv2.sqlite3'
    DEBUG = True
    SECRET_KEY = 'secretkey' 
    JWT_SECRET_KEY = 'jwtsecretkey'