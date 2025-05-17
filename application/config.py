class Config():
    DEBUG = False
    SQLALCHEMY_TRACK_MODIFICATIONS = True

class LocalDevelopmentConfig(Config):
    # basic configuration
    SQLALCHEMY_DATABASE_URI = 'sqlite:///vpv2.sqlite3'
    DEBUG = True
    #security configuration
    SECRET_KEY = 'secretkey'  #this will hash the user's information in screen
    SECURITY_PASSWORD_HASH = 'bcrypt'  #this will hash pwd so that even developer can't see
    SECURITY_PASSWORD_SALT = 'pwdsalt'  #helps to hash pwds
    WTF_CSRF_ENABLED = False  # helps backend make sure that data coming from a form, is actually the form of the same application
    SECURITY_TOKEN_AUTHENTICATION_HEADER = 'Authentication-Token'