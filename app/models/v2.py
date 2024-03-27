#!/usr/bin/env python3
"""hold class TimestampMixin, User, Business and Review which create which 
create table for storing user, business and review data. all classes inherite 
from TimestampMixin to hold date when object created and updated."""

from app import db


class TimestampMixin(object):
    """adds created_at and updated_at timestamps to tables that inherit 
    this class"""
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(
        db.DateTime, 
        server_default=db.func.now(),
        server_onupdate=db.func.now()
        )


class User(TimestampMixin, db.Model):
    """create users table"""
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(128), nullable=False)
    password = db.Column(db.String(128), nullable=False)
    first_name = db.Column(db.String(128))
    last_name = db.Column(db.String(128))
    image = db.Column(db.String(255), default='avatar_2x.png')
    logged_in = db.Column(db.Boolean, default=False)
    businesses = db.relationship(
        'Business', 
        backref='user', 
        cascade='all, delete-orphan'
    )
    reviews = db.relationship(
        'Review',
        backref='user',
        cascade='all, delete-orphan'
    )


class Business(TimestampMixin, db.Model):
    """create businesses table"""
    __tablename__ = 'businesses'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    location = db.Column(db.String(128), nullable=False)
    category = db.Column(db.String(128), nullable=False)
    description = db.Column(db.String(1024))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    reviews = db.relationship(
        'Review',
        backref='business',
        cascade='all, delete-orphan'
    )


class Review(TimestampMixin, db.Model):
    """create review table"""
    __tablename__ = 'reviews'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128))
    review = db.Column(db.String(255))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    business_id = db.Column(db.Integer, db.ForeignKey('businesses.id'))
