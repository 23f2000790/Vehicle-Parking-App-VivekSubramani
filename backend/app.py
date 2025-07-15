from flask import Flask
from application.security import jwt
from application.database import db
from application.config import LocalDevelopmentConfig
from application.models import Users
from werkzeug.security import generate_password_hash
from flask_cors import CORS
from application.celery_init import celery_init_app
from celery.schedules import crontab
from application.caching import cache

app = None

def create_app():
    app = Flask(__name__)
    app.config.from_object(LocalDevelopmentConfig)

    app.config['CACHE_TYPE'] = 'RedisCache'
    app.config['CACHE_DEFAULT_TIMEOUT'] = 300

    db.init_app(app)
    jwt.init_app(app)
    CORS(app)
    cache.init_app(app)
    app.app_context().push()
    return app

app = create_app()
celery = celery_init_app(app)
celery.autodiscover_tasks()

@celery.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(
        crontab(minute='*/2'),
        monthly_report.s(),
    )


from application.routes import *

if __name__ == '__main__':
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

    app.run()
