"""
Serializers for the documents API view.
"""

from rest_framework import serializers

from core.models import (
    Document,
    AuthoredDocument,
    SavedDocument
)


class DocumentSerializer(serializers.ModelSerializer):
    """
    Serializer for document objects.
    """

    class Meta:
        model = Document
        fields = ['id', 'title', 'repository_uri', 'repository_id', 'status']
        read_only_fields = ['id']


class DocumentDetailSerializer(DocumentSerializer):
    """
    Serializer for document detail objects.
    """

    class Meta(DocumentSerializer.Meta):
        fields = DocumentSerializer.Meta.fields + ['created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class AuthoredDocumentSerializer(serializers.ModelSerializer):
    """
    Serializer for authored document objects.
    """
    document = DocumentSerializer(read_only=True)
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = AuthoredDocument
        fields = ('id', 'author', 'document', 'created_at')
        read_only_fields = ('id', 'created_at')


class SavedDocumentSerializer(serializers.ModelSerializer):
    """
    Serializer for saved document objects.
    """
    document = DocumentSerializer(read_only=True)
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = SavedDocument
        fields = ('id', 'user', 'document', 'created_at')
        read_only_fields = ('id', 'created_at')


class RepositoryDocumentSerializer(serializers.Serializer):
    """
    Serializer for repository document objects.
    """
    id = serializers.CharField(max_length=255)
    title = serializers.CharField(max_length=255)
    repository_uri = serializers.CharField(max_length=255)
    repository_id = serializers.CharField(max_length=255)
    status = serializers.CharField(max_length=1)
    author = serializers.CharField(max_length=255, allow_blank=True)
    type = serializers.CharField(max_length=255, allow_blank=True)
    publication_date = serializers.CharField(max_length=255, allow_blank=True)
    knowledge_area = serializers.CharField(max_length=255, allow_blank=True)
    license = serializers.CharField(max_length=255, allow_blank=True)
