#!/usr/bin/python3
"""Test /api/v2/auth/logout api endpoint"""

import json
import jwt
import os
import unittest

from app import create_app
from app.extensions import db
from app.models.v2 import User


class TestUserLogout(unittest.TestCase):
    """Test user logout"""
    def setUp(self):
        """
        set up the testing environment before each test case.
            Creates a Flask app instance for testing, pushes an application
            context,
            initializes a test client, and defines sample user data.
        """
        self.app, _ = create_app("testing")
        self.app.app_context().push()
        self.client = self.app.test_client()

        self.user = {
            "username": "test",
            "password": "Test@12",
            "email": "test@gmail.com",
            "first_name": "murangiri",
            "last_name": "bonface"
        }
        self.register = self.client.post(
            '/api/v2/auth/register',
            data=json.dumps(self.user),
            headers={"content-type": "application/json"})
        self.assertEqual(self.register.status_code, 201)

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

    def test_logout_successful(self):
        """Test successful logout"""
        logout = self.client.post(
            '/api/v2/auth/logout',
            headers={
                "content-type": "application/json",
                "access-token": self.token
            })
        data = jwt.decode(
            self.token, os.getenv("SECRET_KEY"), algorithms=['HS256'])
        current_user = User.query.filter_by(
            username=data['username']).first()
        self.assertEqual(logout.status_code, 200)
        self.assertFalse(current_user.logged_in)

    def test_invalid_access_token(self):
        """test with invalid access token"""
        logout = self.client.post(
            '/api/v2/auth/logout',
            headers={
                "content-type": "application/json",
                "access-token": "invalid_token"
            })
        self.assertEqual(logout.status_code, 401)

    def test_logged_out_user(self):
        """test logout  while already logged out"""
        self.client.post(
            '/api/v2/auth/logout',
            headers={
                "content-type": "application/json",
                "access-token": self.token
            })
        logout = self.client.post(
            '/api/v2/auth/logout',
            headers={
                "content-type": "application/json",
                "access-token": self.token
            })
        self.assertEqual(logout.status_code, 401)
        expected_response = {"message": "You are not logged in"}
        actual_response = json.loads(logout.get_data(as_text=True))
        self.assertEqual(actual_response, expected_response)


if __name__ == "__main__":
    unittest.main()
