#!/usr/bin/python3
"""test for POST /api/v2/businesses/<businessId>/reviews create a new review"""

import uuid
import json
import unittest

from app import create_app
from app.extensions import db
from app.models.v2 import User, Business, Review


class TestCreateBusinessReview(unittest.TestCase):
    """Test creation of a new busines review"""
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

        self.register = self.client.post(
            '/api/v2/auth/register',
            data=json.dumps(self.user),
            headers={"content-type": "application/json"})
        self.assertEqual(self.register.status_code, 201)

        self.register2 = self.client.post(
            '/api/v2/auth/register',
            data=json.dumps(self.user2),
            headers={"content-type": "application/json"})
        self.assertEqual(self.register.status_code, 201)

        self.login = self.client.post(
            '/api/v2/auth/login',
            data=json.dumps({
                "username": "test",
                "password": "Test@12"}),
            headers={"content-type": "application/json"})
        self.assertEqual(self.login.status_code, 200)

        self.login2 = self.client.post(
            '/api/v2/auth/login',
            data=json.dumps({
                "username": "test2",
                "password": "Test@12"}),
            headers={"content-type": "application/json"})
        self.assertEqual(self.login.status_code, 200)

        self.data = json.loads(self.login.get_data(as_text=True))
        self.data2 = json.loads(self.login2.get_data(as_text=True))
        self.token = self.data['access-token']
        self.token2 = self.data2['access-token']

        self.regbiz = self.client.post(
            '/api/v2/businesses',
            data=json.dumps(self.business),
            headers={
                "content-type": "application/json",
                "access-token": self.token
            })
        self.assertEqual(self.regbiz.status_code, 201)
        self.biz = Business.query.first()
        self.bizid = self.biz.id

    def tearDown(self):
        """Tear down the test environment after each test case."""
        with self.app.app_context():
            Review.query.delete()
            Business.query.delete()
            User.query.delete()
            db.session.commit()

    def test_successful_review_creation(self):
        """Test successful creation of a review"""
        response = self.client.post(
            '/api/v2/businesses/{}/reviews'.format(self.bizid),
            data=json.dumps(self.review),
            headers={
                "content-type": "application/json",
                "access-token": self.token2
            })
        self.assertEqual(response.status_code, 201)

    def test_reviewing_own_business(self):
        """Test review creation for the user's own business"""
        response = self.client.post(
            '/api/v2/businesses/{}/reviews'.format(self.bizid),
            data=json.dumps(self.review),
            headers={
                "content-type": "application/json",
                "access-token": self.token
            })
        self.assertEqual(response.status_code, 401)
        expected_response = "you cannot review your own business"
        self.assertIn(expected_response, response.data.decode("utf-8"))

    def test_non_existing_business(self):
        """Test review creation for a non-existing business"""
        response = self.client.post(
            '/api/v2/businesses/{}/reviews'.format(uuid.uuid4()),
            data=json.dumps(self.review),
            headers={
                "content-type": "application/json",
                "access-token": self.token2
            })
        self.assertEqual(response.status_code, 404)
        expected_response = "Business not found"
        self.assertIn(expected_response, response.data.decode("utf-8"))

    def test_exceed_max_review_length(self):
        """Test for exceeding maximum review length"""
        response = self.client.post(
            '/api/v2/businesses/{}/reviews'.format(self.bizid),
            data=json.dumps({
                "title": "test1",
                "review": "test" * 100,
            }),
            headers={
                "content-type": "application/json",
                "access-token": self.token2
            })
        self.assertEqual(response.status_code, 401)
        expected_response = "Review content exceeds the maximum length"
        self.assertIn(expected_response, response.data.decode("utf-8"))


if __name__ == "__main__":
    unittest.main()
