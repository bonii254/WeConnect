#!/usr/bin/env python3
"""manage user authorization and authentications"""


import datetime
import jwt
import os
import random
import string

from flask import Blueprint, jsonify, request
from utils.json_schema import (reg_user_schema, login_schema, reset_pass,
                               update_user_schema, login_required, forgot_pass)
from app.services.mail import send_password_reset_email
from app.models.v2 import User
from app.extensions import db, mail, bcrypt
from cerberus import Validator


auth = Blueprint('auth', __name__, url_prefix="/api/v2")


@auth.route('/auth/register', methods=['POST'], strict_slashes=False)
def create_user():
    """creates a new user"""
    user_info = request.get_json()
    validator = Validator(reg_user_schema)
    validator.validate(user_info)
    errors = validator.errors
    if errors:
        return jsonify({"Errors": errors}), 400
    user_info['username'] = user_info['username'].strip().lower()
    user_info['password'] = bcrypt.generate_password_hash(
        user_info['password']).decode('utf-8')
    new_user = User(**user_info)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({
        "Details": {"username": new_user.username,
                    "first_name": new_user.first_name,
                    "last_name": new_user.last_name,
                    "email": new_user.email}, "Success": "user created!"}), 201


@auth.route('/auth/login', methods=['POST'], strict_slashes=False)
def login():
    """login a user by authentification"""
    try:
        login_info = request.get_json()
        validator = Validator(login_schema)
        validator.validate(login_info)
        errors = validator.errors
        if errors:
            return jsonify({"Errors": errors}), 400
        username = login_info['username'].strip().lower()
        user = User.query.filter_by(username=username).first()
        if not user:
            return jsonify({"message": "username not found"}), 404
        if bcrypt.check_password_hash(user.password, login_info['password']):
            payload = {
                "username": user.username, "email": user.email,
                "first_name": user.first_name, "last_name": user.last_name,
                "image": user.image,
                "exp":
                    datetime.datetime.utcnow() + datetime.timedelta(minutes=60)
                }
            token = jwt.encode(
                payload, os.getenv("SECRET_KEY"), algorithm='HS256')
            user.logged_in = True
            db.session.commit()
            return jsonify({
                "message": "Login successful!",
                "access-token": token
                }), 200
        return jsonify({"message": "incorrect password"}), 401
    except Exception:
        return jsonify({
            "Error": "incorrect information"}), 400


@auth.route('/auth/logout', methods=['POST'], strict_slashes=False)
@login_required
def logout(current_user):
    """logout a user"""
    current_user.logged_in = False
    db.session.commit()
    return jsonify({"message": "logged out"}), 200


@auth.route('/auth/reset-password', methods=['PUT'], strict_slashes=False)
@login_required
def reset_password(current_user):
    """reset the current user password"""
    data = request.get_json()
    validator = Validator(reset_pass)
    validator.validate(data)
    errors = validator.errors
    if errors:
        return jsonify({"Errors": errors}), 401
    if bcrypt.check_password_hash(
            current_user.password, data['old_password']):
        hashed_password = bcrypt.generate_password_hash(
            data['password']).decode('utf-8')
        current_user.password = hashed_password
        db.session.commit()
        return jsonify({"message": "password updated"}), 201

    error = {"old_password": "incorrect old password"}
    return jsonify({"Errors": error}), 401


@auth.route('/auth/update-profile', methods=['PUT'], strict_slashes=False)
@login_required
def update_profile(current_user):
    """updates current user info"""
    user_info = request.get_json()
    validator = Validator(update_user_schema)
    validator.validate(user_info)
    errors = validator.errors
    if errors:
        return jsonify({"Errors": errors}), 401
    current_user.username = user_info['username']
    current_user.email = user_info['email']
    current_user.first_name = user_info['first_name']
    current_user.last_name = user_info['last_name']
    current_user.image = user_info['image']
    db.session.commit()
    return jsonify({
        "Success": "user updated!",
        "Details": {
            "email": current_user.email,
            "username": current_user.username,
            "first_name": current_user.first_name,
            "last_name": current_user.last_name}
    }), 201


@auth.route('/auth/forgot-password', methods=['PUT'], strict_slashes=False)
def forgot_password():
    """recover passord using email"""
    user_info = request.get_json()
    validator = Validator(forgot_pass)
    validator.validate(user_info)
    errors = validator.errors
    if errors:
        return jsonify({"Errors": errors})
    user = User.query.filter_by(email=user_info['email']).first()
    if user:
        characters = string.ascii_letters + string.digits + string.punctuation
        password = ''.join(random.choice(characters) for _ in range(8))
        user.password = bcrypt.generate_password_hash(password).decode('utf-8')
        db.session.commit()
        data = {
            "user_id": user.id,
            "password": password,
            "email": user.email
        }

        send_password_reset_email.delay(data)
        return jsonify({
            "message": "check your email and log in with the new password"
            }), 201
    else:
        return jsonify({
            "Error": "email not found! input email associated with the account"
            }), 404
