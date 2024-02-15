#!/usr/bin/python
""" holds class Location"""
import models
from models.base_model import BaseModel, Base
from os import getenv
import sqlalchemy
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship


class Location(BaseModel, Base):
    """Representation of location """
    if models.storage_t == "db":
        __tablename__ = 'locations'
        name = Column(String(128), nullable=False)
        businesses = relationship("Business",
                              backref="location",
                              cascade="all, delete, delete-orphan")
    else:
        name = ""

    def __init__(self, *args, **kwargs):
        """initializes location"""
        super().__init__(*args, **kwargs)
