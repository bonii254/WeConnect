#!/usr/bin/python3
"""Test suite for the POST /api/v2/auth/register endpoint."""
import os
import logging
import sys
import unittest
import json

"""sys.path.append(
    os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', '..')))"""
from app import create_app
from app.extensions import db
from app.models.v2 import User


class TestUserRegistration(unittest.TestCase):
    """
    Test suite for the POST /api/v2/auth/register endpoint.
    """

    def setUp(self):
        """
        Set up the testing environment before each test case.

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

    def tearDown(self):
        """
        Clean up the testing environment after each test case.
        """
        with self.app.app_context():
            User.query.delete()
            db.session.commit()

    def test_register_user(self):
        """
         Test registering a new user via POST request to the
         /api/v2/auth/register endpoint.
         Ensures that sending a valid user registration request results in the
         creation of a new user in the database.
        """
        initial_count = len(User.query.all())
        response = self.client.post(
            '/api/v2/auth/register',
            data=json.dumps(self.user),
            headers={"content-type": "application/json"})
        final_count = len(User.query.all())
        self.assertEqual(response.status_code, 201)
        self.assertEqual(final_count - initial_count, 1)

    def test_register_existing_user(self):
        """Test registering an existing user."""
        self.client.post(
            '/api/v2/auth/register',
            data=json.dumps(self.user),
            headers={"content-type": "application/json"})
        response = self.client.post(
            '/api/v2/auth/register',
            data=json.dumps(self.user),
            headers={"content-type": "application/json"})
        self.assertEqual(response.status_code, 400)
        expected_message = "Sorry!! username taken!"
        self.assertIn(expected_message, response.data.decode('utf-8'))

    def test_missing_fields(self):
        """Test registering with missing fields."""
        missing_field_user = {
            "first_name": "bonface",
            "last_name": "murangiri"
        }
        res = self.client.post(
            '/api/v2/auth/register',
            data=json.dumps(missing_field_user),
            headers={"content-type": "application/json"})
        expected_message = "required field"
        self.assertIn(expected_message, res.data.decode('utf-8'))

    def test_register_weak_password(self):
        """Test registering with a weak password"""
        self.user["password"] = "test"
        res = self.client.post(
            '/api/v2/auth/register',
            data=json.dumps(self.user),
            headers={"content-type": "application/json"})
        expected_message = (
            "password must be between 6 and 10 characters "
            "with mixture of numbers, alphanumeric and special characters"
            )
        self.assertIn(expected_message, res.data.decode('utf-8'))

    def test_register_duplicate_email(self):
        """Test registering with a duplicate email."""
        duplicate_email_user = {
            "username": "test1",
            "password": "Test@12",
            "email": "test@gmail.com",
            "first_name": "murangiri",
            "last_name": "bonface"
        }
        res = self.client.post(
            'api/v2/auth/register',
            data=json.dumps(self.user),
            headers={"content-type": "application/json"})
        res2 = self.client.post(
            'api/v2/auth/register',
            data=json.dumps(duplicate_email_user),
            headers={"content-type": "application/json"})
        expected_message = "Email taken"
        self.assertIn(expected_message, res2.data.decode('utf-8'))

    def test_register_invalid_email(self):
        """Test registering with invalid email."""
        self.user["email"] = "test.gmail"
        res = self.client.post(
            'api/v2/auth/register',
            data=json.dumps(self.user),
            headers={"content-type": "application/json"})
        expected_message = "Invalid Email"
        self.assertIn(expected_message, res.data.decode('utf-8'))

    def test_register_invalid_username(self):
        """Test registering with an invalid username."""
        self.user["username"] = "12345"
        res = self.client.post(
            'api/v2/auth/register',
            data=json.dumps(self.user),
            headers={"content-type": "application/json"})
        expected_message = "Username cannot contain only numbers"
        self.assertEqual(res.status_code, 400)
        self.assertIn(expected_message, res.data.decode('utf-8'))


if __name__ == "__main__":
    unittest.main()
