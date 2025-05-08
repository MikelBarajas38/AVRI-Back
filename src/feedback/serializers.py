"""
Serializers for the Feedback app.
"""

from rest_framework import serializers

from core.models import SatisfactionSurveyResponse


class SatisfactionSurveyResponseSerializer(serializers.ModelSerializer):
    """
    Serializer for SatisfactionSurveyResponse model.
    """

    class Meta:
        model = SatisfactionSurveyResponse
        fields = ('user', 'survey', 'completed_at')
        read_only_fields = ('user', 'completed_at')
        extra_kwargs = {
            'survey': {'required': True}
        }
