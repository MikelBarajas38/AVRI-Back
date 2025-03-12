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
        Return documents ordered by created_at (newest first).
        Allows ordering by updated_at if specified.
        """
        # TODO: order by created_at, updated_at

        queryset = Document.objects.all().order_by('-created_at')

        order_by = self.request.query_params.get('order_by')
        if order_by == 'update_at':
            queryset = queryset.order_by('-update_at')

        return self.queryset

    def get_serializer_class(self):
        """
        Return appropriate serializer class.
        """
        if self.action == 'retrieve':
            return serializers.DocumentDetailSerializer

        return self.serializer_class
