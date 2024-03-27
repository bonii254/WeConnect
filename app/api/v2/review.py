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
    user_id = current_user.id
    business_id = business.id
    title = review_info['title']
    review = review_info['review']
    new_review = Review(
        user_id=user_id, business_id=business_id, title=title, review=review)
    db.session.add(new_review)
    db.session.commit()
    return jsonify({
        "message": "Review sent",
        "Review": {
            "id": new_review.id, "business_name": business.name,
            "title": new_review.title,
            "review": new_review.review, "user_id": new_review.user_id,
            "business_id": new_review.business_id}}), 201


@review.route(
    'businesses/<businessId>/reviews', methods=['GET'], strict_slashes=False)
def get_business_reviews(businessId):
    """get all reviews for a business"""
    business = Business.query.filter_by(id=businessId).first()
    if not business:
        return jsonify({"message": "Business not found"}), 404
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('limit', 10, type=int)
    my_reviews = Review.query.filter_by(
        business_id=businessId).order_by(Review.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False)
    reviews = my_reviews.items
    if not reviews:
        return jsonify({"message": "No Reviews for this business"})
    return jsonify({
        "message": f"reviews for {business.name}",
        "Details": [
            {
                "id": review.id, "title": review.title,
                "review": review.review, "user_id": review.user_id,
                "business_id": review.business_id
                } for review in reviews],
        "per_page": my_reviews.per_page, "page": my_reviews.page,
        "total": my_reviews.total, "pages": my_reviews.pages,
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
        review.review = review_info['review']
        db.session.commit()
        return jsonify({
            "message": "review updated sucessfully",
            "Details": {
                "id": review.id, "title": review.title,
                "review": review.review, "user_id": review.user_id,
                "business_id": review.business_id
            }}), 200
    return jsonify({"Error": "you can only update your review"})


@review.route(
    'businesses/reviews/<reviewId>', methods=['DELETE'], strict_slashes=False)
@login_required
def delete_business_review(current_user, reviewId):
    review = Review.query.filter_by(id=reviewId).first()
    if review:
        if review.user_id == current_user.id:
            db.session.delete(review)
            db.session.commit()
            return jsonify({"message": "review deleted"}), 200
        return jsonify({"error": "you can only delete your own review"}), 403
    return jsonify({"error": "review not found"}), 404
