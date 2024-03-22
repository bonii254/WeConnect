#!/usr/bin/env python3
"""instantiate mail, celery, Bcrypt and sqlalchemy"""
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_bcrypt import Bcrypt
from celery import Celery

db = SQLAlchemy()
mail = Mail()
bcrypt = Bcrypt()


def make_celery(app):
    celery = Celery(app.import_name)
    celery.conf.update(app.config["CELERY_CONFIG"])

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery
