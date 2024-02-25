#!/usr/bin/python3
"""instantiate mail and sqlalchemy"""

from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail


db = SQLAlchemy()
mail = Mail()
