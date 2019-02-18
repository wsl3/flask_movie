from flask import Flask, render_template
from app.extensions import db, migrate
import app.models  # it is must that make models and db together
from app import config
from app.auth import auth  # blueprint: auth


def create_app(config_name=None):
    app = Flask(__name__)
    app.config.from_object(config)

    app.register_blueprint(auth) # register auth
    db.init_app(app)
    migrate.init_app(app=app, db=db)

    return app
