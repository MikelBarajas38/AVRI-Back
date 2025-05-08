"""
Views for the recommender API.
"""

import os

from rest_framework import viewsets, generics
from rest_framework import authentication, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

from core.models import UserProfile, Document
from core.services.ragflow_service import RAGFlowService

from recommender import serializers

def get_user_profile_string(user_profile: UserProfile) -> str:
    """
    Generate user profile string from the UserProfile object.
    """
    return f"{user_profile.user.username} - {user_profile.profile}"


def get_recommendations(user_profile: UserProfile, max_recommendations: int) -> list:
    """
    Get document recommendations based on user profile.
    """

    #dummy implementation for now
    documents = Document.objects.all()
    recommendations = [document.id for document in documents[:max_recommendations]]
    return recommendations


class CreateUserProfileView(generics.CreateAPIView):
    """
    View for creating user profiles.
    """
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.UserProfileSerializer

    def perform_create(self, serializer):
        """
        Save the user profile with the authenticated user.
        """
        serializer.save(user=self.request.user)

class ManageUserProfileView(generics.RetrieveUpdateAPIView):
    """
    View for managing user profiles.
    """
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.UserProfileSerializer

    def get_object(self):
        """
        Retrieve and return the authenticated user's profile.
        """
        try:
            return UserProfile.objects.get(user=self.request.user)
        except UserProfile.DoesNotExist:
            return None


class DocumentRecommendationViewSet(viewsets.GenericViewSet):
    """
    ViewSet for document recommendations.
    Returns recommended documents based on user profile.
    """
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.RecommendationSerializer

    def get_queryset(self):
        """
        Base queryset for recommendations.
        """
        return Document.objects.all()

    @action(detail=False, methods=['get'])
    def serve(self, request):
        """
        Get document recommendations for the current user.

        Query parameters:
        - max_count: Maximum number of recommendations to return (default: 10)
        """
        max_count = int(request.query_params.get('max_count', 10))

        try:
            user_profile = UserProfile.objects.get(user=request.user)
        except UserProfile.DoesNotExist:
            return Response(
                {'error': 'User profile not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        recommended_ids = get_recommendations(user_profile, max_count)

        documents = Document.objects.filter(id__in=recommended_ids)

        data = {
            'documents': documents,
        }

        serializer = self.get_serializer(data)
        return Response(serializer.data)
