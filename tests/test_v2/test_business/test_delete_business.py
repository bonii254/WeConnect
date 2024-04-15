#!/usr/bin/python3
"""Test DELETE /api/v2/businesses/<businessId> delete business"""

import json
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

    def test_successful_business_deletion(self):
        """Test successful deletion of a business."""
        response = self.client.delete(
            '/api/v2/businesses/' + str(self.biz.id),
            headers={
                "content-type": "application/json",
                "access-token": self.token
            })
        self.assertEqual(response.status_code, 201)
        self.assertIn("business deleted", response.data.decode("utf-8"))

    def test_business_not_found(self):
        """Test deletion of a non-existing business."""
        response = self.client.delete(
            '/api/v2/businesses/' + str(uuid.uuid4()),
            headers={
                "content-type": "application/json",
                "access-token": self.token
            })
        self.assertEqual(response.status_code, 404)
        self.assertIn("business not found", response.data.decode("utf-8"))

    def test_unauthorized_user(self):
        """Test deletion of a business by an unauthorized user."""
        response = self.client.delete(
            '/api/v2/businesses/' + str(self.biz.id),
            headers={
                "content-type": "application/json",
                "access-token": self.token2
            })
        self.assertEqual(response.status_code, 403)
        self.assertIn("only business owner can delete", str(response.data))

    def test_database_state_after_deletion(self):
        """Test the database state after business deletion."""
        initial_count = len(Business.query.all())
        response = self.client.delete(
            '/api/v2/businesses/' + str(self.biz.id),
            headers={
                "content-type": "application/json",
                "access-token": self.token
            })
        final_count = len(Business.query.all())
        deleted_business = Business.query.filter_by(id=self.biz.id).first()
        self.assertIsNone(deleted_business)
        self.assertEqual(initial_count - final_count, 1)


if __name__ == "__main__":
    unittest.main()
