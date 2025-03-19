"""
Tests for models.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model

import core.models as cm


class ModelTests(TestCase):
    """
    Test models
    """

    def test_create_user_with_email_successful(self):
        """
        Test creating a new user with an email is successful
        """
        email = 'test@example.com'
        password = 'testpass1234'

        user = get_user_model().objects.create_user(email, password)

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_created_user_email_normalized(self):
        """
        Test email for a new user is normalized
        """
        sample_emails = [
            ['test1@EXAMPLE.com', 'test1@example.com'],
            ['Test2@Example.com', 'Test2@example.com'],
            ['TEST3@EXAMPLE.COM', 'TEST3@example.com'],
            ['test4@example.COM', 'test4@example.com']
        ]

        password = 'testpass1234'

        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(email, password)
            self.assertEqual(user.email, expected)

    def test_create_user_without_email(self):
        """
        Test creating user without email raises error
        """
        email = None
        password = 'testpass1234'

        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(email, password)

    def test_create_superuser(self):
        """
        Test creating a new superuser
        """
        email = 'test@example.com'
        password = 'testpass1234'

        user = get_user_model().objects.create_superuser(email, password)

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_create_field_of_study(self):
        """
        Test creating a new field of study
        """
        name = 'Test Field'

        field = cm.FieldOfStudy.objects.create(name=name)

        self.assertEqual(str(field), name)

    def test_create_user_full_data(self):
        """
        Test creating a new user with full data
        """
        field = cm.FieldOfStudy.objects.create(name='Test Field')

        payload = {
            'email': 'test@example.com',
            'password': 'testpass1234',
            'name': 'Test Name',
            'first_name': 'Parental',
            'last_name': 'Maternal',
            'education_level': 'L',
            'field_of_study': field
        }

        user = get_user_model().objects.create_user(**payload)

        for k, v in payload.items():
            if k == 'password':
                continue
            self.assertEqual(getattr(user, k), v)

        self.assertTrue(user.check_password(payload['password']))

    def test_create_document(self):
        """
        Test creating a new document
        """
        payload = {
            'title': 'Test Document',
            'repository_uri': 'https://example.com',
        }

        document = cm.Document.objects.create(**payload)

        for k, v in payload.items():
            self.assertEqual(getattr(document, k), v)

    def test_create_document_with_status(self):
        """
        Test creating a new document with status
        """
        payload = {
            'title': 'Test Document',
            'repository_uri': 'https://example.com',
            'status': 'R',
        }

        document = cm.Document.objects.create(**payload)

        for k, v in payload.items():
            self.assertEqual(getattr(document, k), v)
