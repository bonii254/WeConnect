#!/usr/bin/python3
"""Test /api/v2/auth/update-profile endpoint"""

import json
import threading
import unittest

from app import create_app
from app.extensions import db
from app.models.v2 import User


class testUpdateUserProfile(unittest.TestCase):
    """
    Test suite for the 'update-profile' endpoint.
        This class contains test cases to verify the functionality
        of the 'update-profile' endpoint in the authentication API.
    """
    def setUp(self):
        """
        Set up the testing environment before each test case.
            Creates a Flask app instance for testing, pushes an application
            context, initializes a test client, and defines sample user data.
        """
        self.app, _ = create_app("testing")
        self.app.app_context().push
        self.client = self.app.test_client()
        self.user = {
            "username": "test",
            "password": "Test@12",
            "email": "test@gmail.com",
            "first_name": "murangiri",
            "last_name": "bonface"
            }
        response = self.client.post(
            '/api/v2/auth/register',
            data=json.dumps(self.user),
            headers={"content-type": "application/json"})
        self.assertEqual(response.status_code, 201)

        self.login = self.client.post(
            '/api/v2/auth/login',
            data=json.dumps({
                "username": "test",
                "password": "Test@12"}),
            headers={"content-type": "application/json"})
        self.assertEqual(self.login.status_code, 200)

        self.data = json.loads(self.login.get_data(as_text=True))
        self.token = self.data['access-token']

    def tearDown(self):
        """Tear down the test environment after each test case."""
        with self.app.app_context():
            User.query.delete()
            db.session.commit()

    def test_update_profile_success(self):
        """Test successful update of user profile."""
        update_data = {
            "username": "bonii",
            "email": "bonii@gmail.com",
            "first_name": "pizzo",
            "last_name": "tech",
            "image": "updated.jpg"
            }
        response = self.client.put(
            '/api/v2/auth/update-profile',
            data=json.dumps(update_data),
            headers={
                "content-type": "application/json",
                "access-token": self.token
            })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json["Success"], "user updated!")
        with self.app.app_context():
            updated_user = User.query.filter_by(username="bonii").first()
            self.assertIsNotNone(updated_user)
            self.assertEqual(updated_user.email, "bonii@gmail.com")
            self.assertEqual(updated_user.first_name, "pizzo")
            self.assertEqual(updated_user.last_name, "tech")
            self.assertEqual(updated_user.image, "updated.jpg")

    def test_update_profile_unauthorized_access(self):
        """Test unauthorized access when updating profile."""
        update_data = {
            "username": "bonii",
            "email": "bonii@gmail.com",
            "first_name": "pizzo",
            "last_name": "tech",
            "image": "updated.jpg"
        }
        response = self.client.put(
            '/api/v2/auth/update-profile',
            data=json.dumps(update_data),
            headers={
                "content-type": "application/json",
                "access-token": "invalid_token"
            })
        self.assertEqual(response.status_code, 401)


if __name__ == "__main__":
    unittest.main()
