"""
Serializers for the recommender API View.
"""

from rest_framework import serializers

from core.models import UserProfile

from documents.serializers import DocumentSerializer


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for UserProfile model.
    """

    class Meta:
        model = UserProfile
        fields = ('user', 'profile', 'created_at', 'updated_at')
        read_only_fields = ('user', 'created_at', 'updated_at')
        extra_kwargs = {
            'profile': {'required': True}
        }


class RecommendationSerializer(serializers.Serializer):
    """
    Serializer for document recommendation requests.
    """
    documents = DocumentSerializer(many=True, read_only=True)
