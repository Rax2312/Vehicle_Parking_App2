from flask import Flask
from .models import db, User
import os
from dotenv import load_dotenv
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask import request, jsonify
import logging
from datetime import timedelta
from flask_jwt_extended import decode_token
import sys
from flask_caching import Cache
from celery import Celery

load_dotenv()
cache = Cache()

# Global celery instance for CLI and Flask
celery = Celery(
    'app',
    backend='redis://localhost:6379/0',
    broker='redis://localhost:6379/0',
    include=['app.tasks.exports', 'app.tasks.reminders', 'app.tasks.reports']
)

# Configuring celery
celery.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    worker_pool='solo',  
    worker_concurrency=1,  
    task_always_eager=False,  
)


def make_celery(app):
    celery.conf.update(app.config)
    celery.autodiscover_tasks(['app.tasks'])
    TaskBase = celery.Task
    class ContextTask(TaskBase):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    return celery


def create_app():
    app = Flask(__name__, instance_relative_config=True)

    CORS(app, resources={r"/api/*": {"origins": ["http://localhost:8080", "http://127.0.0.1:8080"]}}, supports_credentials=True)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        'sqlite:///' + os.path.join(app.instance_path, 'parking.db')
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'c1f0484f4567848cab07cb334a9d2b86'
    
    # Loading SMTP from environment variables
    app.config['SMTP_HOST'] = os.environ.get('SMTP_HOST', 'smtp.mailtrap.io')
    app.config['SMTP_PORT'] = int(os.environ.get('SMTP_PORT', 2525))
    app.config['SMTP_USER'] = os.environ.get('SMTP_USER', '')
    app.config['SMTP_PASS'] = os.environ.get('SMTP_PASS', '')
    app.config['SMTP_FROM'] = os.environ.get('SMTP_FROM', '22f3002775@ds.study.iitm.ac.in')

    app.config['JWT_SECRET_KEY'] = 'e41064763c722c9f8b2ab59f677e44f5'
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=30)
    app.config['JWT_TOKEN_LOCATION'] = ['headers']              
    app.config['JWT_COOKIE_CSRF_PROTECT'] = False              

    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except OSError:
        pass

    db.init_app(app)
    jwt = JWTManager(app)
    cache.init_app(app)
    app.celery = make_celery(app)

    app.config['PROPAGATE_EXCEPTIONS'] = True

    @jwt.unauthorized_loader
    def custom_unauthorized_response(callback):
        return jsonify({'message': 'Missing or invalid JWT'}), 401

    @jwt.invalid_token_loader
    def custom_invalid_token_response(callback):
        return jsonify({'message': 'Invalid JWT'}), 422

    # Creating admin (default user)
    with app.app_context():
        db.create_all()
        admin = User.query.filter_by(role='admin').first()
        if not admin:
            admin = User(
                first_name='Admin',
                last_name='User',
                age=30,
                username='admin@gmail.com',
                email='admin@gmail.com',
                phone_number='9999999999',
                address='Admin Office',
                role='admin'
            )
            admin.set_password('admin')
            db.session.add(admin)
            db.session.commit()

    # Registering blueprints
    from .api.auth import auth_bp
    from .api.admin import admin_bp
    from .api.user import user_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(user_bp)

    from .tasks import exports, reminders, reports

    @app.errorhandler(500)
    def handle_500(e):
        import traceback
        print("=== 500 ERROR ===")
        print(traceback.format_exc())
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500

    return app
