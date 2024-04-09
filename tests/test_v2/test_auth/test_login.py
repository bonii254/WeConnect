#!/usr/bin/activate
"""Test suite for the /auth/login endpoint."""
import json
import unittest

from app import create_app
from app.extensions import db
from app.models.v2 import User


class TestUserLogin(unittest.TestCase):
    """Test suite for the /auth/login endpoint."""
    def setUp(self):
        """Set up the test environment before each test case."""
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
        response = self.client.post(
            '/api/v2/auth/register',
            data=json.dumps(self.user),
            headers={"content-type": "application/json"})
        self.assertEqual(response.status_code, 201)

    def tearDown(self):
        """Tear down the test environment after each test case."""
        with self.app.app_context():
            User.query.delete()
            db.session.commit()

    def test_login_successful(self):
        """Test login with correct credentials."""
        res = self.client.post(
            '/api/v2/auth/login',
            data=json.dumps({"username": "test", "password": "Test@12"}),
            headers={"content-type": "application/json"}
            )
        self.assertEqual(res.status_code, 200)
        self.assertIn("auth_token", res.data.decode("utf-8"))
        self.assertIn("Login successful!", res.data.decode("utf-8"))

    def test_login_incorrect_password(self):
        """
        Test login with incorrect password.
            Verify that the login endpoint rejects login attempts
            with an incorrect password.
        """
        res = self.client.post(
            '/api/v2/auth/login',
            data=json.dumps({"username": "test", "password": "Test"}),
            headers={"content-type": "application/json"}
            )
        self.assertEqual(res.status_code, 401)
        self.assertIn("incorrect password", res.data.decode("utf-8"))

    def test_login_username_not_found(self):
        """
        Test login with non-existing username.
            Verify that the login endpoint handles login attempts
            with a non-existing username.
        """
        res = self.client.post(
            '/api/v2/auth/login',
            data=json.dumps({"username": "invalid", "password": "Test@12"}),
            headers={"content-type": "application/json"}
            )
        self.assertEqual(res.status_code, 404)
        self.assertIn("username not found", res.data.decode("utf-8"))

    def test_login_missing_fields(self):
        """
        Test login with missing fields.
            Verify that the login endpoint handles login attempts
            with missing required fields.
        """
        res = self.client.post(
            '/api/v2/auth/login',
            data=json.dumps({}),
            headers={"content-type": "application/json"}
            )
        self.assertEqual(res.status_code, 400)
        self.assertIn("required field", res.data.decode("utf-8"))
        self.assertIn("password", res.data.decode("utf-8"))


if __name__ == "__main__":
    unittest.main()
