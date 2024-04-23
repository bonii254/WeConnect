#!/usr/bin/python3
"""Test for DELETE api/v2/businesses/reviews/<reviewId> endpoint."""

import json
import uuid
import unittest

from app import create_app
from app.extensions import db
from app.models.v2 import User, Business, Review


class testUpdateReview(unittest.TestCase):
    """Tests for deleting a review"""
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

    def test_delete_review_successfully(self):
        """Test successfull deletion of a review"""
        response = self.client.delete(
            '/api/v2/businesses/reviews/' + str(self.reviewid),
            headers={
                "content-type": "application/json",
                "access-token": self.token2
            })
        self.assertEqual(response.status_code, 200)
        self.assertIn("review deleted", response.data.decode("utf-8"))

    def test_review_not_found(self):
        """Test deletion of a non-existing review"""
        response = self.client.delete(
            '/api/v2/businesses/reviews/' + str(uuid.uuid4()),
            headers={
                "content-type": "application/json",
                "access-token": self.token2
            })
        self.assertEqual(response.status_code, 404)
        self.assertIn("review not found", response.data.decode("utf-8"))

    def test_unauthorized_user(self):
        """Test deletion of a review by an unauthorized user."""
        response = self.client.delete(
            '/api/v2/businesses/reviews/' + str(self.reviewid),
            headers={
                "content-type": "application/json",
                "access-token": self.token
            })
        expected_response = "you can only delete your own review"
        self.assertEqual(response.status_code, 403)
        self.assertIn(expected_response, response.data.decode("utf-8"))

    def test_database_state_after_review_deletion(self):
        """Test the database state after review deletion."""
        initial_count = len(Business.query.all())
        response = self.client.delete(
            '/api/v2/businesses/reviews/' + str(self.reviewid),
            headers={
                "content-type": "application/json",
                "access-token": self.token2
            })
        final_count = len(Review.query.all())
        deleted_review = Review.query.filter_by(id=self.review.id).first()
        self.assertIsNone(deleted_review)
        self.assertEqual(initial_count - final_count, 1)


if __name__ == "__main__":
    unittest.main()
