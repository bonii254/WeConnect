#!/usr/bin/python3
"""Test PUT /api/v2/businesses/<businessId> Update business"""

import json
import jwt
import os
import unittest
import uuid

from app import create_app
from app.extensions import db
from app.models.v2 import User
from app.models.v2 import Business


class TestGetAllRegisteredBusinesses(unittest.TestCase):
    """test Update business"""
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
        self.business2 = {
            "name": "timtech",
            "location": "chuka",
            "category": "security",
            "description":  "quality services",
        }
        self.updatebusiness = {
            "name": "luxlite",
            "location": "chogoria",
            "category": "entertainment",
            "description":  "event sound systems",
        }
        self.businessdup = self.updatebusiness
        self.register = self.client.post(
            '/api/v2/auth/register',
            data=json.dumps(self.user),
            headers={"content-type": "application/json"})
        self.assertEqual(self.register.status_code, 201)

        self.register2 = self.client.post(
            '/api/v2/auth/register',
            data=json.dumps(self.user2),
            headers={"content-type": "application/json"})
        self.assertEqual(self.register2.status_code, 201)

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
        self.assertEqual(self.login2.status_code, 200)

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

    def tearDown(self):
        """Tear down the test environment after each test case."""
        with self.app.app_context():
            Business.query.delete()
            User.query.delete()
            db.session.commit()

    def test_successfull_business_profile_update(self):
        """test successfull business profile update"""
        response = self.client.put(
            '/api/v2/businesses/' + str(self.biz.id),
            data=json.dumps(self.updatebusiness),
            headers={
                "content-type": "application/json",
                "access-token": self.token
            })
        self.assertEqual(response.status_code, 200)

    def test_update_business_not_found(self):
        """
        Test updating a non-existing business.

        This test case attempts to update a business that does not exist.
        It ensures that the endpoint returns an appropriate error response
        (status code 404) indicating that the business was not found.
        """
        response = self.client.put(
           '/api/v2/businesses/' + str(uuid.uuid4()),
           data=json.dumps(self.updatebusiness),
           headers={
               "content-type": "application/json",
               "access-token": self.token
           })

        self.assertEqual(response.status_code, 404)
        self.assertIn("business not found", response.data.decode("utf-8"))

    def test_update_business_duplicate_name(self):
        """
        Test updating a business with a name that already exists.

        This test case attempts to update a business with a name that already
        exists for another business. It ensures that the endpoint returns
        an appropriate error response (status code 400) indicating
        that the business name is already taken
        """
        self.client.post(
            '/api/v2/businesses',
            data=json.dumps(self.businessdup),
            headers={
                "content-type": "application/json",
                "access-token": self.token
            })
        response = self.client.put(
            '/api/v2/businesses/' + str(self.biz.id),
            data=json.dumps(self.updatebusiness),
            headers={
                "content-type": "application/json",
                "access-token": self.token
            })
        expected_response = "Business name already taken"
        self.assertEqual(response.status_code, 400)
        self.assertIn(expected_response, response.data.decode("utf-8"))

    def test_update_business_unauthorized_user(self):
        """
        Test updating a business by an unauthorized user.

        This test case attempts to update a business where the current user
        is not the owner of the business. It ensures that the endpoint returns
        an appropriate error response (status code 403) indicating that only
        the business owner can update the business.
        """
        self.client.post(
            '/api/v2/businesses',
            data=json.dumps(self.business2),
            headers={
                "content-type": "application/json",
                "access-token": self.token2
            })
        biz = Business.query.filter_by(name="timtech").first()
        response = self.client.put(
            '/api/v2/businesses/' + str(biz.id),
            data=json.dumps(self.updatebusiness),
            headers={
                "content-type": "application/json",
                "access-token": self.token
            })

        expected_response = "only business owner can update"
        self.assertEqual(response.status_code, 403)
        self.assertIn(expected_response, response.data.decode("utf-8"))

    def test_update_business_owner_id_not_modified(self):
        """
        Test that the owner's ID cannot be modified.

        This test case attempts to update the user ID associated
        with the business.
        It ensures that the endpoint does not allow modification of the
        owner's ID.
        """
        self.updatebusiness["id"] = str(uuid.uuid4())
        response = self.client.put(
            '/api/v2/businesses/' + str(self.biz.id),
            data=json.dumps(self.updatebusiness),
            headers={
                "content-type": "application/json",
                "access-token": self.token
            })
        self.assertEqual(response.status_code, 400)
        self.assertIn("unknown field", response.data.decode("utf-8"))


if __name__ == "__main__":
    unittest.main()
