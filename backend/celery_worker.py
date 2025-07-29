from app import create_app

flask_app = create_app()
celery = flask_app.celery

if __name__ == '__main__':
    celery.start() 