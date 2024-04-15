#!/usr/bin/python3
"""Test /api/v2/business api endpoint"""

import json
import jwt
import os
import unittest

from app import create_app
from app.extensions import db
from app.models.v2 import User
from app.models.v2 import Business


class TestCreateBusiness(unittest.TestCase):
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
        self.business = {
            "name": "pizzotech",
            "location": "chuka",
            "category": "networking",
            "description":  "quality services",
        }
        self.emptyfieldbiz = {
            "name": "",
            "location": "",
            "category": "",
            "description": "",
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
            Business.query.delete()
            User.query.delete()
            db.session.commit()

    def test_creaate_business_successfull(self):
        """test successfull business creation"""
        response = self.client.post(
            '/api/v2/businesses',
            data=json.dumps(self.business),
            headers={
                "content-type": "application/json",
                "access-token": self.token})

        self.assertEqual(response.status_code, 201)
        self.assertIn("Business created", response.data.decode('utf-8'))

    def test_business_already_exists(self):
        """Test creating a business that already exists."""
        self.client.post(
            '/api/v2/businesses',
            data=json.dumps(self.business),
            headers={
                "content-type": "application/json",
                "access-token": self.token})
        response = self.client.post(
            '/api/v2/businesses',
            data=json.dumps(self.business),
            headers={
                "content-type": "application/json",
                "access-token": self.token})
        self.assertEqual(response.status_code, 400)
        self.assertIn("Sorry!! name taken!", response.data.decode('utf-8'))

    def test_invalid_access_token(self):
        """Test creating a business with an invalid access token."""
        response = self.client.post(
            '/api/v2/businesses',
            data=json.dumps(self.business),
            headers={
                "content-type": "application/json",
                "access-token": "invalid_token"})
        self.assertEqual(response.status_code, 401)
        expected_response = "Token is invalid or Expired"
        self.assertIn(expected_response, response.data.decode('utf-8'))

    def test_empty_request_body(self):
        """Test creating a business with an empty request body."""
        response = self.client.post(
            '/api/v2/businesses',
            data=json.dumps({}),
            headers={
                "content-type": "application/json",
                "access-token": self.token})
        expected_response = "required field"
        self.assertEqual(response.status_code, 400)
        self.assertIn(expected_response, response.data.decode('utf-8'))

    def test_empty_fields(self):
        """Test creating a business with empty fields."""
        response = self.client.post(
            '/api/v2/businesses',
            data=json.dumps(self.emptyfieldbiz),
            headers={
                "content-type": "application/json",
                "access-token": self.token})
        expected_response = "empty values not allowed"
        self.assertEqual(response.status_code, 400)
        self.assertIn(expected_response, response.data.decode('utf-8'))


if __name__ == "__main__":
    unittest.main()
