#!/usr/bin/python3
""" holds class User"""

import models
from models.base_model import BaseModel, Base
from os import getenv
import sqlalchemy
from sqlalchemy import Column, String, Boolean
from sqlalchemy.orm import relationship
from hashlib import md5


class User(BaseModel, Base):
    """Representation of a user """
    if models.storage_t == 'db':
        __tablename__ = 'users'
        username = Column(String(128), nullable=False)
        email = Column(String(128), nullable=False)
        password = Column(String(128), nullable=False)
        first_name = Column(String(128), nullable=True)
        last_name = Column(String(128), nullable=True)
        image = Column(String,  default="avatar.png")
        logged_in = Column(Boolean, default=False)
        business = relationship("Business",
                                backref="user",
                                cascade='all, delete-orphan')
        reviews = relationship("Review",
                               backref="user",
                               cascade='all, delete-orphan')
    else:
        username = ""
        email = ""
        password = ""
        first_name = ""
        last_name = ""

    def __init__(self, *args, **kwargs):
        """initializes user"""
        super().__init__(*args, **kwargs)

    def __setattr__(self, name, value):
        """sets a password with md5 encryption"""
        if name == "password":
            value = md5(value.encode()).hexdigest()
        super().__setattr__(name, value)


new_user = User(username="boni", email="bonnrangi95@gmail.com", password="qwerty", first_name="boniface", last_name="kaibi")
