"""
Tests for models.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model


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
