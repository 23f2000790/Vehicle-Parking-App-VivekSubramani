from flask_jwt_extended import JWTManager
from application.models import Users

jwt = JWTManager()

@jwt.user_identity_loader
def load_user(user):
    return user.username

@jwt.user_lookup_loader
def user_lookup_callback(jwt_header, jwt_data):
    identity = jwt_data["sub"]
    return Users.query.filter_by(username=identity).one_or_none()
