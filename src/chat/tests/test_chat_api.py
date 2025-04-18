"""
Test the chat API
"""

import os

from unittest.mock import patch

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from core.models import ChatSession

from chat.serializers import (
    ChatSessionSerializer,
    ChatSessionDetailSerializer,
    QuerySerializer
)


CHAT_SESSION_URL = reverse('chat:chat-list')


def detail_url(chat_session_id):
    """
    Return chat session detail URL.
    """
    return reverse('chat:chat-detail', args=[chat_session_id])


def ask_url(chat_session_id):
    """
    Return chat session ask URL.
    """
    return reverse('chat:chat-ask', args=[chat_session_id])


def create_chat_session(**params):
    """
    Helper function to create a sample chat session.
    """
    defaults = {
        'session_id': 'test-session-id',
        'session_name': 'Test-session',
        'user': None,
        'assistant_id':'test-assistant',
    }
    defaults.update(params)
    chat_session = ChatSession.objects.create(**defaults)
    return chat_session


def create_user(**params):
    """
    Helper function to create a user.
    """
    return get_user_model().objects.create_user(**params)


class PrivateChatApiTests(TestCase):
    """
    Test the private features of the chat API (authenticated).
    """

    def setUp(self):
        self.client = APIClient()

        self.user = create_user(
            email='test@example.com',
            password='testpassword'
        )
        self.client.force_authenticate(user=self.user)

    @patch('chat.views.RAGFlowService')
    def test_list_chat_sessions(self, MockRagFlowService):
        """
        Test retrieving a list of chat sessions.
        """
        create_chat_session(user=self.user, session_id='1')
        create_chat_session(user=self.user, session_id='2')

        other_user = create_user(
            email='other@example.com',
            password='otherpassword'
        )
        create_chat_session(user=other_user, session_id='3')

        response = self.client.get(CHAT_SESSION_URL)

        chat_sessions = ChatSession.objects.filter(user=self.user).order_by('-created_at')
        serializer = ChatSessionSerializer(chat_sessions, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data, serializer.data)

    @patch('chat.views.RAGFlowService')
    def test_retrieve_chat_session(self, MockRagFlowService):
        """
        Test retrieving a chat session.
        """
        mock_ragflow = MockRagFlowService.return_value
        mock_ragflow.list_sessions.return_value = {
            'code': 0,
            'data': [
                {'role': 'user', 'content': 'Hello'},
                {'role': 'assistant', 'content': 'Hi there!'}
            ]
        }

        chat_session = create_chat_session(
            user=self.user,
            session_id='1',
            session_name='Test Session'
        )

        url = detail_url(chat_session.session_id)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['session_id'], chat_session.session_id)
        self.assertEqual(response.data['code'], 200)
        self.assertEqual(len(response.data['data']), 2)

        mock_ragflow.list_sessions.assert_called_once_with(
            assistant_id=chat_session.assistant_id,
            session_id=chat_session.session_id
        )

    @patch('chat.views.RAGFlowService')
    def test_retrieve_chat_session_fails(self, MockRagFlowService):
        """
        Test retrieving a chat session fails gracefully, returning available information.
        """
        mock_ragflow = MockRagFlowService.return_value
        mock_ragflow.list_sessions.return_value = {
            'code': 1,
            'message': 'Session not found'
        }

        chat_session = create_chat_session(
            user=self.user,
            session_id='1',
            session_name='Test Session'
        )

        url = detail_url(chat_session.session_id)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['code'], 500)
        self.assertEqual(response.data['detail'], 'Session not found')

    @patch('chat.views.RAGFlowService')
    @patch('chat.views.get_session_name_from_query')
    @patch('chat.views.os.getenv')
    def test_create_chat_session(self, mock_getenv, mock_get_session_name_from_query, MockRagFlowService):
        """
        Test creating a new chat session.
        """
        mock_getenv.return_value = 'test-assistant-id'
        mock_get_session_name_from_query.return_value = 'Test Session'

        mock_ragflow = MockRagFlowService.return_value
        mock_ragflow.create_session.return_value = {
            'code': 0,
            'data': {'id': 'test-session-id'}
        }

        payload = {
            'session_name': 'How do I create a chat session?'
        }

        response = self.client.post(CHAT_SESSION_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['session_id'], 'test-session-id')

        chat_session = ChatSession.objects.get(session_id='test-session-id')
        self.assertEqual(chat_session.session_name, 'Test Session')
        self.assertEqual(chat_session.user, self.user)
        self.assertEqual(chat_session.assistant_id, 'test-assistant-id')

        mock_ragflow.create_session.assert_called_once_with(
            assistant_id='test-assistant-id',
            session_name='Test Session'
        )

        mock_get_session_name_from_query.assert_called_once_with('How do I create a chat session?')

    @patch('chat.views.RAGFlowService')
    @patch('chat.views.get_session_name_from_query')
    @patch('chat.views.os.getenv')
    def test_create_chat_session_fails(self, mock_getenv, mock_get_session_name_from_query, MockRagFlowService):
        """
        Test creating a new chat session fails.
        """
        mock_getenv.return_value = 'test-assistant-id'
        mock_get_session_name_from_query.return_value = 'Test Session'

        mock_ragflow = MockRagFlowService.return_value
        mock_ragflow.create_session.return_value = {
            'code': 1,
            'message': 'Error creating session'
        }

        payload = {
            'session_name': 'How do I create a chat session?'
        }

        response = self.client.post(CHAT_SESSION_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
        self.assertEqual(ChatSession.objects.count(), 0)

    @patch('chat.views.RAGFlowService')
    def test_delete_chat_session(self, MockRagFlowService):
        """
        Test deleting a chat session.
        """
        mock_ragflow = MockRagFlowService.return_value
        mock_ragflow.delete_session.return_value = {
            'code': 0,
            'message': 'Session deleted'
        }

        chat_session = create_chat_session(
            user=self.user,
            session_id='1',
            session_name='Test Session'
        )

        url = detail_url(chat_session.session_id)
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(ChatSession.objects.filter(session_id=chat_session.session_id).exists())

        mock_ragflow.delete_session.assert_called_once_with(
            assistant_id=chat_session.assistant_id,
            session_ids=[chat_session.session_id]
        )

    @patch('chat.views.RAGFlowService')
    def test_delete_chat_session_fails(self, MockRagFlowService):
        """
        Test deleting a chat session fails.
        """
        mock_ragflow = MockRagFlowService.return_value
        mock_ragflow.delete_session.return_value = {
            'code': 1,
            'message': 'Error deleting session'
        }

        chat_session = create_chat_session(
            user=self.user,
            session_id='1',
            session_name='Test Session'
        )

        url = detail_url(chat_session.session_id)
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
        self.assertTrue(ChatSession.objects.filter(session_id=chat_session.session_id).exists())

    @patch('chat.views.RAGFlowService')
    def test_ask(self, MockRagFlowService):
        """
        Test asking a question in a chat session.
        """

        mock_ragflow = MockRagFlowService.return_value
        mock_ragflow.ask.return_value = {
            'code': 0,
            'data': {'answer': 'This is the answer'}
        }

        chat_session = create_chat_session(
            user=self.user,
            session_id='1',
            session_name='Test Session'
        )

        url = ask_url(chat_session.session_id)
        payload = {
            'query': 'What is the answer?'
        }
        response = self.client.post(url, payload)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        updated_session = ChatSession.objects.get(session_id=chat_session.session_id)
        self.assertNotEqual(updated_session.updated_at, chat_session.updated_at)

        mock_ragflow.ask.assert_called_once_with(
            assistant_id=chat_session.assistant_id,
            session_id=chat_session.session_id,
            question='What is the answer?'
        )

    @patch('chat.views.RAGFlowService')
    def test_ask_no_query_fails(self, MockRagFlowService):
        """
        Test asking a question without a query fails.
        """
        mock_ragflow = MockRagFlowService.return_value
        mock_ragflow.ask.return_value = {
            'code': 1,
            'message': 'Error asking question'
        }

        chat_session = create_chat_session(
            user=self.user,
            session_id='1',
            session_name='Test Session'
        )

        url = ask_url(chat_session.session_id)
        payload = {}
        response = self.client.post(url, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], 'Question is required')
