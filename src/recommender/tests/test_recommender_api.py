"""
Test the recommender API
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from core.models import UserProfile


RECOMMEND_CREATE_PROFILE_URL = reverse('create')
RECOMMEND_PROFILE_URL = reverse('me')


def create_user(**params):
    """
    Create and return a new user.
    """
    return get_user_model().objects.create_user(**params)


class PrivateRecommenderApiTests(TestCase):
    """
    Test the private features of the recommender API.
    """

    def setUp(self):
        self.client = APIClient()

        self.user = create_user(
            email='test@example.com',
            password='testpassword'
        )
        self.client.force_authenticate(user=self.user)

    def test_create_user_profile_success(self):
        """
        Test creating a user profile successfully.
        """
        payload = {
            'profile': {
                'interests': ['machine learning', 'data science'],
                'document_titles': ['Deep Learning', 'AI Basics']
            }
        }

        res = self.client.post(
            RECOMMEND_CREATE_PROFILE_URL,
            payload,
            format='json'
        )

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        profile = UserProfile.objects.get(user=self.user)
        self.assertEqual(profile.profile, payload['profile'])

    def test_retrieve_user_profile_success(self):
        """
        Test retrieving the user profile successfully.
        """
        profile_data = {
            'interests': ['machine learning', 'data science'],
            'document_titles': ['Deep Learning', 'AI Basics']
        }
        UserProfile.objects.create(user=self.user, profile=profile_data)

        res = self.client.get(RECOMMEND_PROFILE_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['profile'], profile_data)
