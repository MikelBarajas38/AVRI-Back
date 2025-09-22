"""
Test the recommender API
"""

from unittest.mock import patch

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from core.models import UserProfile, Document


RECOMMEND_CREATE_PROFILE_URL = reverse('create')
RECOMMEND_PROFILE_URL = reverse('me')
RECOMMEND_SERVE_URL = reverse('recommendations-serve')


def create_user(**params):
    """
    Create and return a new user.
    """
    return get_user_model().objects.create_user(**params)


def create_user_profile(user, **params):
    """
    Helper function to create a user profile.
    """
    defaults = {
        'profile': {
            'interests': ['machine learning'],
            'document_titles': ['Deep Learning']
        }
    }
    defaults.update(params)
    return UserProfile.objects.create(user=user, **defaults)


def create_document(**params):
    """
    Helper function to create a sample document.
    """
    defaults = {
        'id': '1',
        'title': 'Test document',
        'repository_uri': 'https://example.com',
        'repository_id': 'repo_1',
        'status': 'L',
    }
    defaults.update(params)
    document = Document.objects.create(**defaults)
    return document


class PublicRecommenderApiTests(TestCase):
    """
    Test the public features of the recommender API (unauthenticated).
    """

    def setUp(self):
        self.client = APIClient()

    def test_auth_required_for_create_profile(self):
        """
        Test that authentication is required to create a profile.
        """
        payload = {
            'profile': {
                'interests': ['machine learning'],
                'document_titles': ['Deep Learning']
            }
        }
        res = self.client.post(
            RECOMMEND_CREATE_PROFILE_URL,
            payload,
            format='json'
        )
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_auth_required_for_retrieve_profile(self):
        """
        Test that authentication is required to retrieve profile.
        """
        res = self.client.get(RECOMMEND_PROFILE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_auth_required_for_recommendations(self):
        """
        Test that authentication is required to get recommendations.
        """
        res = self.client.get(RECOMMEND_SERVE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecommenderApiTests(TestCase):
    """
    Test the private features of the recommender API (authenticated).
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
        self.assertEqual(profile.user, self.user)

    def test_create_duplicate_profile_fails(self):
        """
        Test creating a duplicate profile returns conflict.
        """
        create_user_profile(self.user)

        payload = {
            'profile': {
                'interests': ['new interest'],
                'document_titles': ['New Document']
            }
        }
        res = self.client.post(
            RECOMMEND_CREATE_PROFILE_URL,
            payload,
            format='json'
        )

        self.assertEqual(res.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(res.data['detail'], 'Profile already exists.')

        self.assertEqual(UserProfile.objects.filter(user=self.user).count(), 1)

    def test_retrieve_user_profile_success(self):
        """
        Test retrieving the user profile successfully.
        """
        profile_data = {
            'interests': ['machine learning', 'data science'],
            'document_titles': ['Deep Learning', 'AI Basics']
        }
        create_user_profile(self.user, profile=profile_data)

        res = self.client.get(RECOMMEND_PROFILE_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['profile'], profile_data)

    def test_retrieve_profile_creates_if_not_exists(self):
        """
        Test retrieving profile creates one if it doesn't exist.
        """
        self.assertFalse(UserProfile.objects.filter(user=self.user).exists())

        res = self.client.get(RECOMMEND_PROFILE_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['profile'], {})

        self.assertTrue(UserProfile.objects.filter(user=self.user).exists())

    def test_update_user_profile_success(self):
        """
        Test updating the user profile successfully.
        """
        initial_data = {
            'interests': ['machine learning'],
            'document_titles': ['Deep Learning']
        }
        create_user_profile(self.user, profile=initial_data)

        updated_data = {
            'profile': {
                'interests': ['machine learning', 'robotics', 'NLP'],
                'document_titles': ['Deep Learning', 'Robot Control']
            }
        }
        res = self.client.patch(
            RECOMMEND_PROFILE_URL,
            updated_data,
            format='json'
        )

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['profile'], updated_data['profile'])

        profile = UserProfile.objects.get(user=self.user)
        self.assertEqual(profile.profile, updated_data['profile'])

    def test_partial_update_user_profile(self):
        """
        Test partial update of user profile.
        """
        initial_data = {
            'interests': ['machine learning', 'data science'],
            'document_titles': ['Deep Learning']
        }
        create_user_profile(self.user, profile=initial_data)

        partial_update = {
            'profile': {
                'interests': ['AI', 'quantum computing'],
                'document_titles': ['Deep Learning']
            }
        }
        res = self.client.patch(
            RECOMMEND_PROFILE_URL,
            partial_update,
            format='json'
        )

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(
            res.data['profile']['interests'],
            ['AI', 'quantum computing']
        )

    @patch('recommender.views.get_recommendations')
    def test_get_recommendations_success(self, mock_get_recommendations):
        """
        Test getting recommendations successfully.
        """
        profile_data = {
            'interests': ['machine learning', 'data science'],
            'document_titles': ['1', '2']
        }
        create_user_profile(self.user, profile=profile_data)

        create_document(id='1', title='ML Guide')
        create_document(id='2', title='Data Science Handbook')
        create_document(id='3', title='Other Document')

        mock_get_recommendations.return_value = ['1', '2']

        res = self.client.get(RECOMMEND_SERVE_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('documents', res.data)
        self.assertEqual(len(res.data['documents']), 2)

        mock_get_recommendations.assert_called_once()
        args = mock_get_recommendations.call_args[0]
        self.assertEqual(args[0].user, self.user)
        self.assertEqual(args[1], 10)  # default max_count

    @patch('recommender.views.get_recommendations')
    def test_get_recommendations_with_max_count(
        self,
        mock_get_recommendations
    ):
        """
        Test getting recommendations with custom max_count parameter.
        """
        create_user_profile(self.user)

        for i in range(10):
            create_document(id=f'{i}', title=f'Document {i}')

        mock_get_recommendations.return_value = ['0', '1', '2', '3', '4']

        res = self.client.get(f'{RECOMMEND_SERVE_URL}?max_count=5')

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        mock_get_recommendations.assert_called_once()
        args = mock_get_recommendations.call_args[0]
        self.assertEqual(args[1], 5)

    def test_get_recommendations_no_profile(self):
        """
        Test getting recommendations when user has no profile.
        """
        # Ensure no profile exists
        self.assertFalse(UserProfile.objects.filter(user=self.user).exists())

        res = self.client.get(RECOMMEND_SERVE_URL)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(res.data['error'], 'User profile not found')

    @patch('recommender.views.RAGFlowService')
    def test_get_recommendations_ragflow_integration(self, MockRagFlowService):
        """
        Test the actual get_recommendations function with RAGFlow integration.
        """
        from recommender.views import get_recommendations

        profile_data = {
            'interests': ['machine learning', 'data science'],
            'document_titles': ['Deep Learning', 'AI Basics']
        }
        user_profile = create_user_profile(self.user, profile=profile_data)

        mock_ragflow = MockRagFlowService.return_value
        mock_ragflow.get_chunks.side_effect = [
            # interest 1
            {
                'code': 0,
                'data': {
                    'chunks': [
                        {'document_id': '1'},
                        {'document_id': '2'}
                    ]
                }
            },
            # interest 2
            {
                'code': 0,
                'data': {
                    'chunks': [
                        {'document_id': '3'},
                        {'document_id': '2'}  # Duplicate
                    ]
                }
            },
            # chunk 1
            {
                'code': 0,
                'data': {
                    'chunks': [
                        {'document_id': '4'}
                    ]
                }
            },
            # chunk 2
            {
                'code': 0,
                'data': {
                    'chunks': [
                        {'document_id': '5'}
                    ]
                }
            }
        ]

        recommendations = get_recommendations(
            user_profile,
            max_recommendations=10
        )

        self.assertEqual(len(set(recommendations)), len(recommendations))
        for i in range(1, 6):
            self.assertIn(f'{i}', recommendations)

        self.assertEqual(mock_ragflow.get_chunks.call_count, 4)

    @patch('recommender.views.RAGFlowService')
    def test_get_recommendations_respects_max_limit(self, MockRagFlowService):
        """
        Test that get_recommendations respects the max_recommendations limit.
        """
        from recommender.views import get_recommendations

        profile_data = {
            'interests': ['machine learning'],
            'document_titles': []
        }
        user_profile = create_user_profile(self.user, profile=profile_data)

        mock_ragflow = MockRagFlowService.return_value
        mock_ragflow.get_chunks.return_value = {
            'code': 0,
            'data': {
                'chunks': [
                    {'document_id': f'{i}'} for i in range(20)
                ]
            }
        }

        recommendations = get_recommendations(
            user_profile,
            max_recommendations=5
        )
        self.assertLessEqual(len(recommendations), 5)

    @patch('recommender.views.RAGFlowService')
    def test_get_recommendations_handles_ragflow_errors(
        self,
        MockRagFlowService
    ):
        """
        Test that get_recommendations handles RAGFlow errors gracefully.
        """
        from recommender.views import get_recommendations

        profile_data = {
            'interests': ['machine learning', 'data science'],
            'document_titles': []
        }
        user_profile = create_user_profile(self.user, profile=profile_data)

        mock_ragflow = MockRagFlowService.return_value
        mock_ragflow.get_chunks.side_effect = [
            # First interest - success
            {
                'code': 0,
                'data': {
                    'chunks': [
                        {'document_id': '1'}
                    ]
                }
            },
            # Second interest - error
            {
                'code': 1,
                'message': 'Error retrieving chunks'
            }
        ]

        recommendations = get_recommendations(
            user_profile,
            max_recommendations=10
        )

        self.assertIn('1', recommendations)
        self.assertEqual(len(recommendations), 1)

    def test_other_user_cannot_access_profile(self):
        """
        Test that users cannot access other users' profiles.
        """
        create_user_profile(self.user)

        other_user = create_user(
            email='other@example.com',
            password='otherpassword'
        )
        self.client.force_authenticate(user=other_user)

        res = self.client.get(RECOMMEND_PROFILE_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['profile'], {})

        self.assertEqual(UserProfile.objects.count(), 2)
