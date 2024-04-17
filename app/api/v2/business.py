#!/usr/bin/python3
"""busines api endpoints"""
from flask import Blueprint, jsonify, request, url_for
from cerberus import Validator
import os
from utils.json_schema import new_business, business_update, login_required
from utils.validations import search
from app.models.v2 import Business
from app.extensions import db


business = Blueprint('business', __name__, url_prefix="/api/v2")


@business.route('/businesses', methods=['POST'], strict_slashes=False)
@login_required
def register_business(current_user):
    """create a new business"""
    bus_info = request.get_json()
    validator = Validator(new_business)
    validator.validate(bus_info)
    errors = validator.errors
    if errors:
        return jsonify({"Errors": errors}), 400
    bus_info['name'] = bus_info['name'].strip().lower()
    bus_info['user_id'] = current_user.id
    new_bus = Business(
        name=bus_info['name'],
        user_id=bus_info['user_id'],
        location=bus_info['location'],
        category=bus_info['category'],
        description=bus_info['description']
    )
    db.session.add(new_bus)
    db.session.commit()
    return jsonify({
        "message": "Business created", "business":
        {
            "name": new_bus.name, "business_id": new_bus.id,
            "description": new_bus.description, "category": new_bus.category,
            "location": new_bus.location, "owner": current_user.username,
        }}), 201


@business.route(
    '/businesses/<business_id>', methods=['GET'], strict_slashes=False)
def get_business(business_id):
    """get one specified business"""
    business = Business.query.filter_by(id=business_id).first()
    if business:
        return jsonify({
            "id": business.id, "user_id": business.user.id,
            "name": business.name, "location": business.location,
            "category": business.category, "description": business.description,
            "created_at": business.created_at,
            "updated_at": business.updated_at,
        })
    return jsonify({"message": "Business not found"}), 404


@business.route('/businesses/user', methods=['GET'], strict_slashes=False)
@login_required
def get_user_businesses(current_user):
    """get list of all current_user businesses"""
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 3, type=int)
    results = Business.query.filter_by(user_id=current_user.id).paginate(
        page=page, per_page=per_page, error_out=False)

    businesses_data = [{
            "id": business.id, "user_id": business.user.id,
            "name": business.name, "location": business.location,
            "category": business.category, "description": business.description,
            "created_at": business.created_at,
            "updated_at": business.updated_at,
        } for business in results.items]

    next_page = url_for(
        'business.get_user_businesses', page=results.next_num) \
        if results.has_next else None
    prev_page = url_for(
        'business.get_user_businesses', page=results.prev_num) \
        if results.has_prev else None
    return jsonify({
        "results": businesses_data,
        "per_page": results.per_page,
        "page": results.page,
        "total_pages": results.pages,
        "total_results": results.total,
        "next_page": next_page,
        "prev_page": prev_page
    }), 200


@business.route('/businesses', methods=['GET'], strict_slashes=False)
def get_all_businesses():
    """return all registered businesses"""
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)

    businesses = Business.query.paginate(
        page=page, per_page=per_page, error_out=False)

    businesses_data = [{
        "id": business.id, "user_id": business.user.id, "name": business.name,
        "location": business.location, "category": business.category,
        "description": business.description, "created_at": business.created_at,
        "updated_at": business.updated_at
    } for business in businesses.items]

    next_page = url_for(
        'business.get_all_businesses', page=businesses.next_num) \
        if businesses.has_next else None

    prev_page = url_for(
        'business.get_all_businesses', page=businesses.prev_num) \
        if businesses.has_prev else None

    return jsonify({
        "results": businesses_data,
        "per_page": businesses.per_page,
        "page": businesses.page,
        "total_pages": businesses.pages,
        "total_results": businesses.total,
        "next_page": next_page,
        "prev_page": prev_page
    }), 200


@business.route('/businesses/search', methods=['GET'], strict_slashes=False)
def search_businesses():
    """search for business by name location and  or category"""
    search_params = {
        'page': request.args.get('page', 1, type=int),
        'name': request.args.get('q', None, type=str),
        'location': request.args.get('location', None, type=str),
        'category': request.args.get('category', None, type=str),
        'limit': request.args.get('limit', 10, type=int),
    }
    results = search(search_params)
    all_businesses = results.items
    return jsonify({
        "page": results.page,
        "total_results": results.total,
        "total_pages": results.pages,
        "per_page": results.per_page,
        "objects": [{
            "id": business.id, "user_id": business.user.id,
            "name": business.name, "location": business.location,
            "category": business.category, "description": business.description,
            "created_at": business.created_at,
            "updated_at": business.updated_at,
        } for business in all_businesses]
        }), 200


@business.route(
    '/businesses/<businessId>', methods=['PUT'], strict_slashes=False)
@login_required
def update_business(current_user, businessId):
    """updates business info"""
    business = Business.query.filter_by(id=businessId).first()
    if not business:
        return jsonify({"message": "business not found"}), 404
    bus_info = request.get_json()
    validator = Validator(business_update)
    validator.validate(bus_info)
    errors = validator.errors
    if errors:
        return jsonify({"Errors": errors}), 400
    duplicate = Business.query.filter(
        Business.name.ilike(bus_info['name'])).first()
    if duplicate and duplicate.id != business.id:
        return jsonify({"Error": "Business name already taken"}), 400
    if business.user.id == current_user.id:
        business.name = bus_info["name"]
        business.category = bus_info["category"]
        business.description = bus_info["description"]
        business.location = bus_info["location"]
        db.session.commit()
        return jsonify({
            "message": "Business updated",
            "Details": {
                "name": business.name, "location": business.location,
                "category": business.category,
                "description": business.description}}), 200
    return jsonify({"message": "only business owner can update"}), 403


@business.route(
    '/businesses/<businessId>', methods=['DELETE'], strict_slashes=False)
@login_required
def delete_business(current_user, businessId):
    """delete business in the database"""
    business = Business.query.filter_by(id=businessId).first()
    if not business:
        return jsonify({"message": "business not found"}), 404
    if business.user.id == current_user.id:
        db.session.delete(business)
        db.session.commit()
        return jsonify({"message": "business deleted"}), 201
    return jsonify({"message": "only business owner can delete"}), 403
