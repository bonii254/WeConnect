#!/usr/bin/python3
"""validation schemas for POST and PUT json data"""


import datetime
import jwt
import os
from functools import wraps
from app.models.v2 import User
from flask import jsonify, request
from werkzeug.security import generate_password_hash, check_password_hash
from utils.validations import (validate_field, validate_email, username_taken,
                                validate_password, forgot_password,)


reg_user_schema = {
    "username": {
        "type": "string",
        "required": True,
        "validator": validate_field
    },
    "email": {
        "type": "string",
        "required": True,
        "validator": validate_email
    },
    "password": {
        "type": "string",
        "required": True,
        "empty": False,
        "validator": validate_password
    },
    "first_name": {
        "type": "string",
        "required": True,
        "empty": False,
    },
    "last_name": {
        "type": "string",
        "required": True,
        "empty": False,
    }
}
#update user schema
update_user_schema = {
    'username': {
        'type': 'string',
        'required': True,
        'empty': False
    },
    'email': {
        'type': 'string',
        'required': True,
        'empty': False,
    },
    'first_name': {
        'type': 'string',
        'required': True,
        'empty': False,
    },
    'last_name': {
        'type': 'string',
        'required': True,
        'empty': False,
    },
    'image': {
        'type': 'string',
        'required': True,
        'empty': False,
    }
}
# login data schema. will validate login data
login_schema = {
    "username": {
        'type': 'string',
        'required': True,
        'validator': username_taken
    },
    "password": {
        'type': 'string',
        'required': True
    }
}
# reset-password data schema

reset_pass = {
    "password": {
        'type': 'string',
        'validator': validate_password,
        'required': True
    },
    "old_password": {
        'type': 'string',
        'required': True
    }
}

new_business = {
    "name": {
        'type': 'string',
        'required': True,
        'empty': False,
        'validator': validate_field
    },
    "location": {
        'type': 'string',
        'required': True,
        'empty': False
    },
    "category": {
        'type': 'string',
        'required': True,
        'empty': False
    },
    "description": {
        'type': 'string',
        'required': True,
        'empty': False
    }
}
business_update = {
    "name": {
        'type': 'string',
        'required': True,
        'empty': False
    },
    "location": {
        'type': 'string',
        'required': True,
        'empty': False
    },
    "category": {
        'type': 'string',
        'required': True,
        'empty': False
    },
    "description": {
        'type': 'string',
        'required': True,
        'empty': False
    }
}
review_schema = {
    "review": {
        'type': 'string',
        'required': True,
        'empty': False
    },
    "title": {
        'type': 'string',
        'required': True,
        'empty': False
    }
}
forgot_pass ={
    'email': {
        'type': 'string',
        'required': True,
        'empty': False,
        'validator': forgot_password
    },
}


def login_required(original_function):
    """
    login decorator function
    it checks the authentication token verify if its valid,
    then return the aunthenticated user
    """
    @wraps(original_function)
    def decorated(*args, **kwargs):
        token = None
        if 'access-token' not in request.headers:
            return jsonify({
                'message': 'Token is missing, login to get token'
            }), 401
        try:
            token = request.headers['access-token']
            data = jwt.decode(token, os.getenv("SECRET_KEY"))
            current_user = User.query.filter_by(
                username=data['username'],
                logged_in=True
            ).first()
            if not current_user:
                return jsonify({"message": "You are not logged in"}), 401
        except Exception as e:
            return jsonify({'message': 'Token is invalid or Expired!'}), 401
        return original_function(current_user, *args, **kwargs)
    return decorated
