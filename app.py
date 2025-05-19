from flask import Flask
from application.database import db
from application.config import LocalDevelopmentConfig
from application.models import Users
from flask_security import Security, SQLAlchemyUserDatastore, hash_password

def create_app():
    app = Flask(__name__)
    app.config.from_object(LocalDevelopmentConfig)
    db.init_app(app)
    app.app_context().push()
    return app

app = create_app()

with app.app_context():
    db.create_all()

    admin = Users.query.filter_by(type='admin').first()
    if not admin:
        first = Users(
            email="admin@admin.com",
            username="admin",
            password="admin123",  
            phone_no="1234567890",
            type="admin",
            status=True
        )
        db.session.add(first)
        db.session.commit()


if __name__ == '__main__':
    app.run()