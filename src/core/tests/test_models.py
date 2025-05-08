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

    def test_create_anonymous_user(self):
        """
        Test creating a new anonymous user
        """
        payload = {
            'is_anonymous': True,
            'name': 'Anonymous User',
            'password': 'testpass1234'
        }

        user = get_user_model().objects.create_user(**payload)
        self.assertTrue(user.is_anonymous)
        self.assertIsNotNone(user.anonymous_id)

    def test_create_document(self):
        """
        Test creating a new document
        """
        payload = {
            'id': '12345',
            'title': 'Test Document',
            'repository_uri': 'https://example.com',
            'repository_id': 'repo_1',
        }

        document = cm.Document.objects.create(**payload)

        for k, v in payload.items():
            self.assertEqual(getattr(document, k), v)

    def test_create_document_with_status(self):
        """
        Test creating a new document with status
        """
        payload = {
            'id': '12345',
            'title': 'Test Document',
            'repository_uri': 'https://example.com',
            'repository_id': 'repo_1',
            'status': 'R',
        }

        document = cm.Document.objects.create(**payload)

        for k, v in payload.items():
            self.assertEqual(getattr(document, k), v)

    def test_create_authored_document(self):
        """
        Test creating a new authored document
        """
        user = get_user_model().objects.create_user(
            email='author@example.com',
            password='testpass1234'
        )

        document = cm.Document.objects.create(
            id='12345',
            title='Test Document',
            repository_uri='https://example.com',
            repository_id='repo_1'
        )

        authored_document = cm.AuthoredDocument.objects.create(
            author=user,
            document=document
        )

        self.assertEqual(authored_document.author, user)
        self.assertEqual(authored_document.document, document)
        self.assertIsNotNone(authored_document.created_at)

    def test_create_saved_document(self):
        """
        Test creating a new saved document
        """
        user = get_user_model().objects.create_user(
            email='author@example.com',
            password='testpass1234'
        )

        document = cm.Document.objects.create(
            id='12345',
            title='Test Document',
            repository_uri='https://example.com',
            repository_id='repo_1'
        )

        saved_document = cm.SavedDocument.objects.create(
            user=user,
            document=document
        )

        self.assertEqual(saved_document.user, user)
        self.assertEqual(saved_document.document, document)
        self.assertIsNotNone(saved_document.created_at)

    def test_create_chat_session(self):
        """
        Test creating a new chat session
        """
        user = get_user_model().objects.create_user(
            email='test@example.com',
            password='testpass1234'
        )

        session = cm.ChatSession.objects.create(
            session_id='12345',
            session_name='Test Session',
            user=user,
            assistant_id='assistant_1'
        )

        self.assertEqual(session.session_id, '12345')
        self.assertEqual(session.session_name, 'Test Session')
        self.assertEqual(session.user, user)

    def test_create_sus_survey_response(self):
        """
        Test creating a new satisfaction survey response
        """
        user = get_user_model().objects.create_user(
            email='test@example.com',
            password='testpass1234'
        )

        payload = {
            'user': user,
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
            },
        }

        survey_response = cm.SatisfactionSurveyResponse.objects.create(
            **payload
        )

        self.assertEqual(survey_response.user, user)
        self.assertEqual(survey_response.version, payload['version'])
        self.assertEqual(
            survey_response.survey,
            payload['survey']
        )
        self.assertIsNotNone(survey_response.completed_at)

    def test_create_user_profile(self):
        """
        Test creating a new user profile
        """
        user = get_user_model().objects.create_user(
            email='test@example.com',
            password='testpass1234'
        )

        payload = {
            'user': user,
            'profile': {
                'bio': 'This is a test bio.',
                'keywords': ['python', 'django'],
                'interests': ['coding', 'reading'],
            }
        }

        user_profile = cm.UserProfile.objects.create(**payload)
        self.assertEqual(user_profile.user, user)
        self.assertEqual(user_profile.profile, payload['profile'])
        self.assertIsNotNone(user_profile.created_at)
        self.assertIsNotNone(user_profile.updated_at)
