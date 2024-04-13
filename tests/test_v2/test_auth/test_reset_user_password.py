#!/usr/bin/python3
"""Test /api/v2/auth/reset-password endpoint"""

import json
import threading
import unittest

from app import create_app
from app.extensions import db
from app.models.v2 import User


class testResetUserPassword(unittest.TestCase):
    """
    Test suite for the 'reset_password' endpoint.
        This class contains test cases to verify the functionality
        of the 'reset_password' endpoint in the authentication API.
        It covers various scenarios such as successful password reset,
        unauthorized access, validation errors, and incorrect old password.
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

    def test_successful_password_reset(self):
        """Test successful password reset."""
        reset = self.client.put(
            '/api/v2/auth/reset-password',
            data=json.dumps({
                "old_password": "Test@12", "password": "N3w@p@ss"}),
            headers={
                "content-type": "application/json",
                "access-token": self.token
            })
        self.assertEqual(reset.status_code, 201)
        expected_response = {"message": "password updated"}
        actual_response = json.loads(reset.get_data(as_text=True))
        self.assertEqual(expected_response, actual_response)

    def test_incorrect_old_password(self):
        """test with wrong old password"""
        incorrect_pass = self.client.put(
            '/api/v2/auth/reset-password',
            data=json.dumps({
                "old_password": "wrong_old_pass", "password": "N3w@p@ss"}),
            headers={
                "content-type": "application/json",
                "access-token": self.token
            })
        self.assertEqual(incorrect_pass.status_code, 401)
        expected_response = {
            "Errors":
            {"old_password": "incorrect old password"}}
        actual_response = json.loads(incorrect_pass.get_data(as_text=True))
        self.assertEqual(expected_response, actual_response)

    def test_invalid_new_password(self):
        """Test resetting password with weak password"""
        weak_pass = self.client.put(
            '/api/v2/auth/reset-password',
            data=json.dumps({
                "old_password": "Test@12", "password": "weak"}),
            headers={
                "content-type": "application/json",
                "access-token": self.token
            })
        self.assertEqual(weak_pass.status_code, 401)

    def reset_password_request(self, client, token, result):
        """Function to send a reset password request."""
        response = self.client.put(
            '/api/v2/auth/reset-password',
            data=json.dumps({
                "old_password": "Test@12", "password": "Str0ngP@ss"}),
            headers={
                "content-type": "application/json",
                "access-token": self.token
            })
        result.append(response.status_code)

    def test_concurrent_requests(self):
        """Test concurrent requests to reset passwords from multiple users."""
        num_requests = 5
        threads = []
        result = []
        for _ in range(num_requests):
            thread = threading.Thread(
                target=self.reset_password_request,
                args=(self.client, self.token, result)
                )
            threads.append(thread)
            thread.start()
        for thread in threads:
            thread.join()
        for response_code in result:
            self.assertEqual(response_code, 201)


if __name__ == "__main__":
    unittest.main()
