#!/usr/bin/env python3


from flask import Flask, Blueprint, make_response, render_template, jsonify
import os
from instance.config import app_config
from flask_migrate import Migrate
from flask_cors import CORS
from .extensions import db, mail, bcrypt, make_celery
from app.api.v2.business import business
from app.api.v2.review import review
from app.api.v2.user import auth


def page_not_found(e):
    return jsonify({
        "Error": "The page you are trying to access was not found."
        }), 404


def create_app(config_name):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(app_config[config_name])
    cors = CORS(app, resources={r"app/api/v2/*": {"origins": "*"}})
    app.config.from_pyfile("config.py")
    app.register_blueprint(business)
    app.register_blueprint(review)
    app.register_blueprint(auth)
    app.config["CELERY_CONFIG"] = {
        "broker_url": "redis://localhost:6379/0", 
        "result_backend": "redis://localhost:6379/0"
     }

    migrate = Migrate(app, db)
    db.init_app(app)
    mail.init_app(app)
    bcrypt.init_app(app)
    
    celery = make_celery(app)
    celery.set_default()
    
    return app, celery


import app.models.v2
