#!/usr/bin/python3
"""api endpoints for reviews"""

from flask import Blueprint, jsonify, request
import os
from cerberus import Validator
from utils.json_schema import (login_required, review_schema)
from app.models.v2 import Review, Business
from app.extensions import db


review = Blueprint('reviews', __name__, url_prefix="/api/v2")


@review.route(
    '/businesses/<businessId>/reviews', methods=['POST'], strict_slashes=False)
@login_required
def create_review(current_user, businessId):
    """create a reiew for business"""
    business = Business.query.filter_by(id=businessId).first()
    if not business:
        return jsonify({"message": "Business not found"}), 404
    if business.user == current_user:
        return jsonify({"Error": "you cannot review your own business"}), 401
    review_info = request.get_json()
    validator = Validator(review_schema)
    validator.validate(review_info)
    errors = validator.errors
    if errors:
        return jsonify({"Errors": errors}), 401
    review_info['user_id'] = current_user.id
    review_info['business_id'] = business.id
    new_review = Review(**review_info)
    db.session.add(new_review)
    db.session.commit()
    return jsonify({
        "message": "Review sent",
        "Review": {
            "id": new_review.id, "title": new_review.title,
            "body": new_review.body, "user_id": new_review.user_id,
            "business_id": new_review.business_id}}), 201


@review.route(
    'businesses/<businessId>/reviews', methods=['GET'], strict_slashes=False)
def get_business_reviews(businessId):
    """get all reviews for a business"""
    business = Business.query.filter_by(id=businessId).first()
    if not business:
        return jsonify({"message": "Business not found"}), 404
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 10, type=int)
    reviews = Review.query.filter_by(
        business_id=businessId).order_by(Review.created_at.desc()).paginate(
            page, limit, False).items
    if not reviews:
        return jsonify({"message": "No Reviews for this business"})
    return jsonify({
        "message": f"reviews for {business}",
        "Details": [
            {
                "id": review.id, "title": review.title,
                "body": review.body, "user_id": review.user_id,
                "business_id": review.business_id
                } for review in reviews]
     }), 200


@review.route(
    'businesses/reviews/<reviewId>', methods=['PUT'], strict_slashes=False)
@login_required
def update_business_reviews(current_user, reviewId):
    """edit business review"""
    review = Review.query.filter_by(id=reviewId).first()
    if not review:
        return jsonify({"message": "review not found"})
    review_info = request.get_json()
    validator = Validator(review_schema)
    validator.validate(review_info)
    errors = validator.errors
    if errors:
        return jsonify({"Errors": errors})
    if review.user == current_user:
        review.title = review_info['title']
        review.body = review_info['body']
        db.session.commit()
        return jsonify({
            "message": "review updated sucessfully",
            "Details": {
                "id": review.id, "title": review.title,
                "body": review.body, "user_id": review.user_id,
                "business_id": review.business_id
            }}), 200
    return jsonify({"Error": "you can only update your review"})
