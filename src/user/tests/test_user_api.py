"""
Tests for the user API.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from user.serializers import UserSerializer

from core.models import FieldOfStudy


CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')
LIST_URL = reverse('user:list')


def create_user(**params):
    """
    Helper function to create a user.
    """
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    """
    Test the public features of the user API (unauthenticated).
    """

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_success(self):
        """
        Test creating user with valid payload is successful.
        """
        payload = {
            'email': 'test@example.com',
            'password': 'testpass1234',
            'name': 'Test Name',
            'first_name': 'Parental',
        }

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        user = get_user_model().objects.get(email=payload['email'])

        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_create_user_with_email_exists_error(self):
        """
        Test creating a user that already exists fails.
        """
        payload = {
            'email': 'test@example.com',
            'password': 'testpass1234',
            'name': 'Test Name',
            'first_name': 'Parental',
        }

        create_user(**payload)

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_user_with_short_password_error(self):
        """
        Test creating a user with a password that is too short fails.
        """
        payload = {
            'email': 'test@example.com',
            'password': '1234',
            'name': 'Test Name',
            'first_name': 'Parental',
        }

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        user = get_user_model().objects.filter(email=payload['email'])

        self.assertFalse(user.exists())

    def test_create_token_for_user(self):
        """
        Test that a token is created for the user.
        """
        payload = {
            'email': 'test@example.com',
            'password': '1234',
            'name': 'Test Name',
            'first_name': 'Parental',
        }

        create_user(**payload)

        payload = {
            'email': 'test@example.com',
            'password': '1234',
        }

        res = self.client.post(TOKEN_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('token', res.data)

    def test_create_token_invalid_credentials(self):
        """
        Test that token is not created if invalid credentials are given.
        """
        payload = {
            'email': 'test@example.com',
            'password': 'goodpass',
            'name': 'Test Name',
            'first_name': 'Parental',
        }

        create_user(**payload)

        payload = {
            'email': 'test@example.com',
            'password': 'badpass',
        }

        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_blank_password(self):
        """
        Test that token is not created if password is blank.
        """
        payload = {
            'email': 'test@example.com',
            'password': '',
        }

        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_profile_unauthorized(self):
        """
        Test that authentication is required for users.
        """
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_all_users(self):
        """
        Test retrieving list of registered users
        """

        create_user(**{
            'email': 'test@example.com',
            'password': 'password1234',
            'name': 'Test Name 1'
        })

        create_user(**{
            'email': 'test2@example.com',
            'password': 'password1234',
            'name': 'Test Name 2'
        })

        users = get_user_model().objects.all()
        serializer = UserSerializer(users, many=True)

        res = self.client.get(LIST_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)


class PrivateUserApiTests(TestCase):
    """
    Test the private features of the user API (authenticated).
    """

    def setUp(self):

        self.client = APIClient()

        field = FieldOfStudy.objects.create(name='Test Field')

        payload = {
            'email': 'test@example.com',
            'password': 'testpass1234',
            'name': 'Test Name',
            'first_name': 'Parental',
            'last_name': 'Maternal',
            'education_level': 'L',
            'field_of_study': field
        }

        self.user = create_user(**payload)
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self):
        """
        Test retrieving profile for logged in user.
        """
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'email': self.user.email,
            'name': self.user.name,
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
            'education_level': self.user.education_level,
            'field_of_study': self.user.field_of_study.id,
        })

    def test_post_me_not_allowed(self):
        """
        Test that POST is not allowed on the me URL.
        """
        res = self.client.post(ME_URL, {})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """
        Test updating the user profile for authenticated user.
        """
        payload = {
            'name': 'New Name',
            'password': 'newpass1234',
        }

        res = self.client.patch(ME_URL, payload)

        self.user.refresh_from_db()

        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
