#!/usr/bin/python3
"""Test /api/v2/business api endpoint get all businesses"""

import json
import jwt
import os
import unittest

from app import create_app
from app.extensions import db
from app.models.v2 import User
from app.models.v2 import Business


class TestGetAllRegisteredBusinesses(unittest.TestCase):
    """test  get all registered businesses"""
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

        self.regbiz = self.client.post(
            '/api/v2/businesses',
            data=json.dumps(self.business),
            headers={
                "content-type": "application/json",
                "access-token": self.token
            })
        self.assertEqual(self.regbiz.status_code, 201)

    def tearDown(self):
        """Tear down the test environment after each test case."""
        with self.app.app_context():
            Business.query.delete()
            User.query.delete()
            db.session.commit()

    def test_list_all_registered_businesses(self):
        """Test list all registered businesses"""
        response = self.client.get(
            '/api/v2/businesses',
            headers={"content-type": "application/json"})
        self.assertEqual(response.status_code, 200)
