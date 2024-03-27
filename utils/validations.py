#!/usr/bin/python3
"""put and post data validation methods"""

import re
from app.models.v2 import User, Business


def validate_field(field, value, error):
    """validate if username is taken"""
    value = value.strip().lower()
    tables = {"username": User, "name": Business}
    queries = {}
    if field == "username":
        if value.isnumeric():
            error(field, "Username cannot contain only numbers")
        queries[field] = [User.username.ilike(value)]
    else:
        queries[field] = [Business.name.ilike(value)]
    if not value:
        error(field, "Field cannot be empty")
    error(field, "Sorry!! %s taken!" % (field)) if tables[field].query.filter(
        *queries[field]).first() else ""


def validate_email(field, value, error):
    """validate if email is not taken and is in correct format"""
    if User.query.filter_by(email=value).first():
        error(field, "Email taken")
    if not re.match(
            r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]{2,4}$', value):
        error(field, "Invalid Email")


def username_taken(field, value, error):
    """validate if the username is already taken"""
    username = value.strip().lower()
    if not username:
        error(field, "Field cannot be empty")
    if not User.query.filter_by(username=username).first():
        error(field, "Sorry!! Username not found!")


def validate_password(field, value, error):
    """validate password"""
    pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d]{6,}$'
    if not re.match(pattern, value):
        error(
            field,
            "password must be more than 6 characters long with numbers,"
            "lowercase and uppercase letters"
        )


def forgot_password(field, value, error):
    """verify if email is registered before sending a new password"""
    pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]{2,4}$'
    if not re.match(pattern, value):
        error(field, "Invalid Email")
    if not User.query.filter_by(email=value).first():
        error(field, "Email does not exist!")


def search(filters):
    """
    Method to perform serch on businesses
    using either name location or category
    """
    category = filters["category"]
    name = filters["name"]
    location = filters["location"]
    page = filters["page"]
    per_page = filters['limit']
    query = []
    if name:
        query.append(Business.name.ilike("%" + name + "%"))
    if category:
        query.append(Business.category.ilike("%" + category + "%"))
    if location:
        query.append(Business.location.ilike("%" + location + "%"))
    businesses = Business.query.filter(*query).paginate(page = page, per_page = per_page, error_out = False)

    return businesses
