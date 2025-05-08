"""
Test the feedback API.
"""

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APIClient

from core.models import SatisfactionSurveyResponse


FEEDBACK_URL = reverse('feedback:feedback-list')


def create_user(**params):
    """
    Helper function to create a user.
    """
    return get_user_model().objects.create_user(**params)



class PublicFeedbackApiTests(TestCase):
    """
    Test the public feedback API (Unauthenticated).
    """

    def setUp(self):
        """
        Create sample feedback for testing.
        """
        self.client = APIClient()

    def test_create_feedback(self):
        """
        Test creating feedback.
        """
        payload = {
            'version': '1.0',
            'survey': {
                'q1': 4,
                'q2': 2,
                'q3': 4,
                'q4': 3,
                'q5': 5,
                'q6': 2,
                'q7': 4,
                'q8': 3,
                'q9': 4,
                'q10': 2,
                'comments': 'Smooth experience, minor issues.'
            } # User should be set in the view
        }
        res = self.client.post(FEEDBACK_URL, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class FeedbackApiTests(TestCase):
    """
    Test the feedback API (Authenticated).
    """

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(**{
             'email': 'test@example.com',
            'password': 'testpass1234',
        })
        self.client.force_authenticate(user=self.user)

    def test_create_feedback(self):
        """
        Test creating feedback.
        """
        payload = {
            'version': '1.0',
            'survey': {
                'q1': 4,
                'q2': 2,
                'q3': 4,
                'q4': 3,
                'q5': 5,
                'q6': 2,
                'q7': 4,
                'q8': 3,
                'q9': 4,
                'q10': 2,
                'comments': 'Smooth experience, minor issues.'
            }
        }
        res = self.client.post(FEEDBACK_URL, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        feedback = SatisfactionSurveyResponse.objects.get(
            user=self.user,
            version=payload['version']
        )
        self.assertEqual(feedback.user, self.user)
        self.assertEqual(feedback.version, payload['version'])
        self.assertEqual(
            feedback.survey,
            payload['survey']
        )
        self.assertIsNotNone(feedback.completed_at)

    def test_get_past_feedback(self):
        """
        Test retrieving past feedback.
        """
        payload = {
            'version': '1.0',
            'survey': {
                'q1': 4,
                'q2': 2,
                'q3': 4,
                'q4': 3,
                'q5': 5,
                'q6': 2,
                'q7': 4,
                'q8': 3,
                'q9': 4,
                'q10': 2,
                'comments': 'Smooth experience, minor issues.'
            }
        }
        self.client.post(FEEDBACK_URL, payload, format='json')
        res = self.client.get(FEEDBACK_URL, format='json')
        feedback = SatisfactionSurveyResponse.objects.filter(
            user=self.user
        ).order_by('-completed_at')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), len(feedback))
        self.assertEqual(res.data[0]['survey'], feedback[0].survey)
