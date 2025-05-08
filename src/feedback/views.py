"""
Views for the feedback app.
"""

from rest_framework import viewsets, mixins
from rest_framework import authentication, permissions

from core.models import SatisfactionSurveyResponse

from feedback.serializers import (
    SatisfactionSurveyResponseSerializer,
)


class SatisfactionSurveyResponseViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet
):
    """
    Viewset for SatisfactionSurveyResponse model.
    """
    serializer_class = SatisfactionSurveyResponseSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    queryset = SatisfactionSurveyResponse.objects.all()

    def get_queryset(self):
        """
        Retrieve and return the satisfaction survey responses.
        """
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        """
        Save the satisfaction survey response with the current user.
        """
        serializer.save(user=self.request.user)
