import os

from flask import Flask, render_template
from flask_pymongo import PyMongo
from flask_login import LoginManager


mongo = PyMongo()
login_manager = LoginManager()


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object('config.DevConfig')

    mongo.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth_bp.login'
    login_manager.login_message_category = 'error'
    login_manager.refresh_view = 'auth_bp.login'
    login_manager.needs_refresh_message_category = 'error'

    with app.app_context():
        from . import routes
        from . import auth

        app.register_blueprint(auth.auth_bp)
        app.register_blueprint(routes.main_bp)

        from app.plotlydash.dash import create_dashboard
        app = create_dashboard(app)

        return app