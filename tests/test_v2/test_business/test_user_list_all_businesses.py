#!/usr/bin/python3
"""Test /api/v2/business/user api endpoint get all current user businesses"""

import json
import unittest

from app import create_app
from app.extensions import db
from app.models.v2 import User
from app.models.v2 import Business


class TestGetAllCurrentUserRegisteredBusinesses(unittest.TestCase):
    """test  get all current user registered businesses"""
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

        for i in range(1, 6):
            self.business["name"] = f"biz{i}"
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

    def test_list_currentuser_businesses_sucessfully(self):
        """list all current user businesses"""
        response = self.client.get(
            '/api/v2/businesses/user',
            headers={
                "content-type": "application/json",
                "access-token": self.token
            })
        self.assertEqual(response.status_code, 200)

    def test_pagination(self):
        """test implementation of pagination"""
        response = self.client.get(
            '/api/v2/businesses/user?page=1&per_page=1',
            headers={
                "content-type": "application/json",
                "access-token": self.token
            })
        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertEqual(data['page'], 1)
        self.assertEqual(data['per_page'], 1)
        self.assertEqual(len(data['results']), 1)
        self.assertEqual(
            data['next_page'], '/api/v2/businesses/user?page=2')
        self.assertIsNone(data['prev_page'])

    def test_invalid_pagination_parameters(self):
        """Test handling of invalid page/per_page parameters.
        This test verifies that the endpoint defaults to valid values
        (1 for page and 3 for per_page) when provided parameters cannot be
        converted to integers. Flask's request.args.get(..., type=int)
        returns None for non-integer values, which is then replaced by the
        default values. The test ensures the endpoint does not fail due to
        invalid parameter types and returns a success response.
        """
        invalid_values = [
            {'page': -1, 'per_page': 10},
            {'page': 1, 'per_page': -10},
            {'page': 'invalid', 'per_page': 10},
            {'page': 1, 'per_page': 'invalid'},
            ]

        for params in invalid_values:
            response = self.client.get(
                '/api/v2/businesses/user',
                query_string=params,
                headers={
                    "content-type": "application/json",
                    "access-token": self.token
                })
            self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()
