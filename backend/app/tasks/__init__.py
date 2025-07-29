from flask import current_app

def get_celery():
    return current_app.celery 
