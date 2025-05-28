from flask import Flask
from flask_jwt_extended import JWTManager
from application.database import db
from application.config import LocalDevelopmentConfig
from application.models import Users
from werkzeug.security import generate_password_hash
from flask_security import Security, SQLAlchemyUserDatastore, hash_password

jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(LocalDevelopmentConfig)

    db.init_app(app)
    jwt.init_app(app)

    with app.app_context():
        db.create_all()

        admin = Users.query.filter_by(type='admin').first()
        if not admin:
            first = Users(
                email="admin@admin.com",
                username="admin",
                password=generate_password_hash("admin123"),  
                phone_no="1234567890",
                type="admin",
                status=True
            )
            db.session.add(first)
            db.session.commit()
    a = input()
    
    return app


if __name__ == '__main__':
    app = create_app()
    app.run()