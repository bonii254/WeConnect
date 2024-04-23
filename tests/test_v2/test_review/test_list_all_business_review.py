#!/usr/bin/python3
"""Test for GET api/v2/businesses/<businessId>/reviews endpoint."""

import json
import uuid
import unittest

from app import create_app
from app.extensions import db
from app.models.v2 import User, Business, Review


class testUpdateReview(unittest.TestCase):
    """Tests for get all reviews for a business"""
    def setUp(self):
        """
        set up the testing environment before each test case.
            Creates a Flask app instance for testing, pushes an application
            context,
            initializes a test client, and defines sample user data.
        """
        self.app, _ = create_app('testing')
        self.app.app_context().push()
        self.client = self.app.test_client()

        self.user = {
            "username": "test",
            "password": "Test@12",
            "email": "test@gmail.com",
            "first_name": "murangiri",
            "last_name": "bonface"
        }

        self.user2 = {
            "username": "test2",
            "password": "Test@12",
            "email": "test2@gmail.com",
            "first_name": "murangiri",
            "last_name": "bonface"
        }

        self.business = {
            "name": "pizzotech",
            "location": "chuka",
            "category": "networking",
            "description":  "quality services",
        }

        self.review = {
            "title": "test review",
            "review": "my test review",
        }

        self.registeruser = self.client.post(
            'api/v2/auth/register',
            data=json.dumps(self.user),
            headers={"content-type": "application/json"})
        self.assertEqual(self.registeruser.status_code, 201)

        self.registeruser2 = self.client.post(
            'api/v2/auth/register',
            data=json.dumps(self.user2),
            headers={"content-type": "application/json"})
        self.assertEqual(self.registeruser.status_code, 201)

        self.loginuser = self.client.post(
            'api/v2/auth/login',
            data=json.dumps({
                "username": "test",
                "password": "Test@12",
            }),
            headers={"content-type": "application/json"})
        self.assertEqual(self.loginuser.status_code, 200)

        self.loginuser2 = self.client.post(
            'api/v2/auth/login',
            data=json.dumps({
                "username": "test2",
                "password": "Test@12",
            }),
            headers={"content-type": "application/json"})
        self.assertEqual(self.loginuser2.status_code, 200)

        self.data = json.loads(self.loginuser.get_data(as_text=True))
        self.data2 = json.loads(self.loginuser2.get_data(as_text=True))
        self.token = self.data["access-token"]
        self.token2 = self.data2["access-token"]

        self.regbiz = self.client.post(
            '/api/v2/businesses',
            data=json.dumps(self.business),
            headers={
                "content-type": "application/json",
                "access_token": self.token})
        self.assertEqual(self.regbiz.status_code, 201)
        self.biz = Business.query.first()
        self.bizid = self.biz.id

        self.postreview = self.client.post(
            '/api/v2/businesses/{}/reviews'.format(self.bizid),
            data=json.dumps(self.review),
            headers={
                "content-type": "application/json",
                "access-token": self.token2
            })
        self.assertEqual(self.postreview.status_code, 201)
        self.review = Review.query.first()
        self.reviewid = self.review.id

    def tearDown(self):
        """Tear down the test environment after each test case."""
        with self.app.app_context():
            Review.query.delete()
            Business.query.delete()
            User.query.delete()
            db.session.commit()

    def test_list_business_review_sucessfully(self):
        """Test list all business reviews"""
        response = self.client.get(
            'api/v2/businesses/{}/reviews'.format(self.bizid),
            headers={"content-type": "application/json"})
        expected_response = "reviews for {}".format(self.biz.name)
        self.assertEqual(response.status_code, 200)
        self.assertIn(expected_response, response.data.decode("utf-8"))

    def test_business_without_review(self):
        """Test a business that has no review"""
        with self.app.app_context():
            Review.query.filter_by(business_id=self.bizid).delete()
            db.session.commit()
        response = self.client.get(
            'api/v2/businesses/{}/reviews'.format(self.bizid),
            headers={"content-type": "application/json"})
        expected_response = "No Reviews for this business"
        self.assertEqual(response.status_code, 404)
        self.assertIn(expected_response, response.data.decode("utf-8"))

    def test_business_not_found(self):
        """Test getting reviews for non existing business"""
        response = self.client.get(
            'api/v2/businesses/{}/reviews'.format(uuid.uuid4()),
            headers={"content-type": "application/json"})
        expected_response = "Business not found"
        self.assertEqual(response.status_code, 404)
        self.assertIn(expected_response, response.data.decode("utf-8"))


if __name__ == "__main__":
    unittest.main()
