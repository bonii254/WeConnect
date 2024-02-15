#!/usr/bin/python
""" holds class Category"""
import models
from models.base_model import BaseModel, Base
from os import getenv
import sqlalchemy
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship


class Category(BaseModel, Base):
    """Representation of category """
    if models.storage_t == "db":
        __tablename__ = 'categories'
        name = Column(String(128), nullable=False)
        businesses = relationship("Business",
                              backref="categories",
                              cascade="all, delete, delete-orphan")
    else:
        state_id = ""
        name = ""

    def __init__(self, *args, **kwargs):
        """initializes category"""
        super().__init__(*args, **kwargs)
