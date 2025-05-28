class Config():
    DEBUG = False
    SQLALCHEMY_TRACK_MODIFICATIONS = True

class LocalDevelopmentConfig(Config):
    # basic configuration
    SQLALCHEMY_DATABASE_URI = 'sqlite:///vpv2.sqlite3'
    DEBUG = True
    #security configuration
    SECRET_KEY = 'secretkey'  #this will hash the user's information in screen
    WTF_CSRF_ENABLED = False  # helps backend make sure that data coming from a form, is actually the form of the same application
    JWT_SECRET_KEY = 'jwtsecretkey'