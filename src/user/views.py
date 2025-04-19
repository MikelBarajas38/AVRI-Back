"""
Views for the user API.
"""

from rest_framework import generics, authentication, permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from django.contrib.auth import get_user_model

from user.serializers import (
    UserSerializer,
    AnonymousUserSerializer,
    AuthTokenSerializer,
    AnonymousAuthTokenSerializer
)


class CreateUserView(generics.CreateAPIView):
    """
    Create a new user in the system.
    """
    serializer_class = UserSerializer


class CreateAnonymousUserView(generics.CreateAPIView):
    """
    Create a new anonymous user in the system.
    """
    serializer_class = AnonymousUserSerializer


class CreateTokenView(ObtainAuthToken):
    """
    Create a new auth token for the user.
    """
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class CreateAnonymousTokenView(ObtainAuthToken):
    """
    Create a new auth token for the anonymous user.
    """
    serializer_class = AnonymousAuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class ManageUserView(generics.RetrieveUpdateAPIView):
    """
    Manage the authenticated user.
    """
    serializer_class = UserSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """
        Retrieve and return the authenticated user.
        """
        return self.request.user

    def get_serializer_class(self):
        if self.request.user.is_anonymous:
            return AnonymousUserSerializer
        return UserSerializer


class ListUsersView(generics.ListAPIView):
    """
    List all registered users
    """
    serializer_class = UserSerializer
    queryset = get_user_model().objects.filter(is_anonymous=False)
