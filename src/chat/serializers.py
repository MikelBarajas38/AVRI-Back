"""
Serializers for the chat API View.
"""

from rest_framework import serializers

from core.models import ChatSession


class ChatSessionSerializer(serializers.ModelSerializer):
    """
    Serializer for chat session objects.
    """
    class Meta:
        model = ChatSession
        fields = ['session_id', 'session_name', 'user']
        read_only_fields = ['session_id', 'user']
        extra_kwargs = {
            'session_name': {'required': True, 'allow_blank': False}
        }


class ChatSessionDetailSerializer(ChatSessionSerializer):
    """
    Serializer for chat session detail objects.
    """
    class Meta(ChatSessionSerializer.Meta):
        fields = ChatSessionSerializer.Meta.fields + ['created_at', 'updated_at']
        read_only_fields = ['session_id', 'user', 'created_at', 'updated_at']


class QuerySerializer(serializers.Serializer):
    """
    Serializer for user query requests.
    """
    query = serializers.CharField(
        max_length=1000,
        required=True,
        allow_blank=False
    )
