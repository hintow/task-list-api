from flask import Flask
from .db import db, migrate
from .models import task
from .routes.task_routes import tasks_bp
import os

def create_app(config = None):
    app = Flask(__name__)

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI')
    #'postgresql+psycopg2://postgres:postgres@localhost:5432/task_list_api_development'

    if config:
        app.config.update(config)
    
    db.init_app(app)
    migrate.init_app(app, db)

    app.register_blueprint(tasks_bp)

    return app