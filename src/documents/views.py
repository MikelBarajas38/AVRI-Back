"""
Views for the documents API
"""

from rest_framework import viewsets

from core.models import Document
from documents import serializers


class DocumentViewSet(viewsets.ModelViewSet):
    """
    Manage documents in the database
    """
    serializer_class = serializers.DocumentSerializer
    queryset = Document.objects.all()

    def get_queryset(self):
        """
        Return documents by date.
        """
        # TODO: order by created_at, updated_at
        return self.queryset

    def get_serializer_class(self):
        """
        Return appropriate serializer class.
        """
        if self.action == 'retrieve':
            return serializers.DocumentDetailSerializer

        return self.serializer_class
