"""
Serializers for the documents API view.
"""

from rest_framework import serializers

from core.models import Document


class DocumentSerializer(serializers.ModelSerializer):
    """
    Serializer for document objects.
    """

    class Meta:
        model = Document
        fields = ['id', 'title', 'repository_uri', 'status']
        read_only_fields = ['id']


class DocumentDetailSerializer(DocumentSerializer):
    """
    Serializer for document detail objects.
    """

    class Meta(DocumentSerializer.Meta):
        fields = DocumentSerializer.Meta.fields + ['created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
