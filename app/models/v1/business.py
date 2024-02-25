#!/usr/bin/python
""" holds class Business"""
import models
from models.base_model import BaseModel, Base
from os import getenv
import sqlalchemy
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship


class Business(BaseModel, Base):
    """Representation of business """
    if models.storage_t == 'db':
        __tablename__ = 'businesses'
        user_id = Column(String(60), ForeignKey('users.id'), nullable=False)
        location = Column(String(128), nullable=False)
        category = Column(String(128), nullable=False)
        name = Column(String(128), nullable=False)
        description = Column(String(1024), nullable=True)
        reviews = relationship("Review",
                               backref="business",
                               cascade="all, delete, delete-orphan")
    else:
        category_id = ""
        location_id = ""
        user_id = ""
        description = ""
        name = ""

    def __init__(self, *args, **kwargs):
        """initializes Place"""
        super().__init__(*args, **kwargs)

    if models.storage_t != 'db':
        @property
        def reviews(self):
            """getter attribute returns the list of Review instances"""
            from models.review import Review
            review_list = []
            all_reviews = models.storage.all(Review)
            for review in all_reviews.values():
                if review.place_id == self.id:
                    review_list.append(review)
            return review_list
