from rest_framework.permissions import BasePermission


class IsAuthor(BasePermission):
    """
    Custom permission to only allow authors.
    """

    def has_permission(self, request, view):
        """
        Check if the user is the author of the document.
        """
        if request.user.is_authenticated and request.user.is_author:
            return True
        return False


class isRegisteredUser(BasePermission):
    """
    Custom permission to only allow registered users.
    """

    def has_permission(self, request, view):
        """
        Check if the user is a registered user.
        """
        if request.user.is_authenticated and not request.user.is_anonymous:
            return True
        return False


class IsRegisteredOrAnonymousUser(BasePermission):
    """
    Custom permission to only allow anonymous users.
    """

    def has_permission(self, request, view):
        """
        Check if the user is an anonymous user.
        """
        if request.user.is_authenticated and request.user.is_anonymous:
            return True
        return False
