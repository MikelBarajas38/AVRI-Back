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
        'session_id': 'test-session',
        'session_name': 'Test Session',
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
            username='testuser',
            password='testpassword'
        )
        self.client.force_authenticate(user=self.user)

    @patch('chat.views.RAGFlowService')
    def test_list_chat_sessions(self, mock_ragflow):
        """
        Test retrieving a list of chat sessions.
        """
        create_chat_session(user=self.user)
        create_chat_session(user=self.user)

        other_user = create_user(
            username='otheruser',
            password='otherpassword'
        )
        create_chat_session(user=other_user)

        response = self.client.get(CHAT_SESSION_URL)

        chat_sessions = ChatSession.objects.filter(user=self.user)
        serializer = ChatSessionSerializer(chat_sessions, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)
