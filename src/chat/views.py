"""
Views for the chat API.
"""

import os

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from rest_framework import authentication, permissions

from core.models import ChatSession
from core.services.ragflow_service import RAGFlowService

from chat import serializers

from chat.exceptions import RagflowException


def get_session_name_from_query(query: str) -> str:
    """
    Generate chat title from the query string.
    """
    ragflow = RAGFlowService()

    try:

        titler_session_response = ragflow.create_session(
            assistant_id=os.getenv('RAGFLOW_TITLER_ID'),
            session_name=query
        )

        if titler_session_response.get('code') != 0:
            raise Exception(
                titler_session_response.get(
                    'message',
                    'Error creating session'
                )
            )

        session_id = titler_session_response['data']['id']

        title_response = ragflow.ask(
            assistant_id=os.getenv('RAGFLOW_TITLER_ID'),
            question=query,
            session_id=session_id
        )

        if title_response.get('code') != 0:
            raise Exception(
                title_response.get(
                    'message',
                    'Error getting title'
                )
            )

        title = title_response['data']['answer']

        ragflow.delete_session(
            assistant_id=os.getenv('RAGFLOW_TITLER_ID'),
            session_ids=[session_id]
        )

        title = ''.join(filter(lambda x: x.isalpha() or x.isspace(), title))
        title = title[:100]
        title = title.strip()

        return title

    except Exception as e:

        raise Exception(f'Failed to get chat title: {str(e)}')


class ChatSessionViewSet(viewsets.ModelViewSet):
    """
    Manage chat sessions in the database.
    """
    serializer_class = serializers.ChatSessionSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'post', 'delete']
    queryset = ChatSession.objects.all()

    def get_serializer_class(self):
        """
        Return appropriate serializer class.
        """
        if self.action == 'retrieve':
            return serializers.ChatSessionDetailSerializer
        elif self.action == 'ask':
            return serializers.QuerySerializer
        return self.serializer_class

    def get_queryset(self):
        """
        Return only the authenticated user's chat sessions
        ordered by created_at (newest first).
        """
        user_queryset = self.queryset.filter(user=self.request.user)
        return user_queryset.order_by('-created_at')

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve a chat session and its messages from RAGFlow.
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = serializer.data

        ragflow = RAGFlowService()

        try:

            messages_response = ragflow.list_sessions(
                assistant_id=instance.assistant_id,
                session_id=instance.session_id
            )

            if messages_response.get('code') != 0:
                raise Exception(
                    messages_response.get(
                        'message',
                        'Error retrieving messages'
                    )
                )

            data['code'] = 200
            data['data'] = messages_response.get('data', [])

            return Response(data)

        except Exception as e:

            data['code'] = 500
            data['data'] = []
            data['detail'] = str(e)
            return Response(data)

    def perform_create(self, serializer):
        """
        Create a new chat session both in the database and through RAGFlow API.
        """

        ragflow = RAGFlowService()
        session_name = serializer.validated_data.get('session_name')

        try:

            session_name = get_session_name_from_query(session_name)

            response = ragflow.create_session(
                assistant_id=os.getenv('RAGFLOW_ASSISTANT_ID'),
                session_name=session_name
            )

            if response.get('code') != 0:
                raise Exception(
                    response.get(
                        'message',
                        'Error creating session'
                    )
                )

            session_id = response['data']['id']

            serializer.save(
                user=self.request.user,
                assistant_id=os.getenv('RAGFLOW_ASSISTANT_ID'),
                session_id=session_id,
                session_name=session_name,
            )

        except Exception as e:

            raise RagflowException(
                f'Failed to create chat session: {str(e)}'
            )

    def perform_destroy(self, instance):
        """
        Delete a chat session both from the database and through RAGFlow API.
        """
        ragflow = RAGFlowService()

        try:

            response = ragflow.delete_session(
                assistant_id=instance.assistant_id,
                session_ids=[instance.session_id]
            )

            if response.get('code') != 0:
                raise Exception(
                    response.get(
                        'message',
                        'Error deleting session'
                    )
                )

            instance.delete()

        except Exception as e:

            raise RagflowException(
                f'Failed to delete chat session: {str(e)}'
            )

    @action(detail=True, methods=['post'])
    def ask(self, request, pk=None):
        """
        Ask a question to the assistant in the specified session.
        """
        session = self.get_object()
        question = request.data.get('query')

        if not question:
            return Response(
                {'detail': 'Question is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        ragflow = RAGFlowService()

        try:

            response = ragflow.ask(
                assistant_id=session.assistant_id,
                session_id=session.session_id,
                question=question
            )

            session.save(update_fields=['updated_at'])

            return Response(response)

        except Exception as e:

            return Response(
                {'detail': f'Failed to get completion: {str(e)}'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
