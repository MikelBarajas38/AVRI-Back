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
