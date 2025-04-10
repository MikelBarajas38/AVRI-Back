"""
Views for the documents API
"""

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter

from core.models import (
    Document
)

from documents import serializers


class DocumentViewSet(viewsets.ModelViewSet):
    """
    Manage documents in the database
    """
    serializer_class = serializers.DocumentSerializer
    queryset = Document.objects.all()
    http_method_names = ['get']
    filter_backends = [OrderingFilter]
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']

    def get_queryset(self):
        """
        Return documents ordered by created_at (newest first).
        Allows ordering by updated_at if specified.
        """
        queryset = Document.objects.all()

        order_by = self.request.query_params.get('ordering', '-created_at')
        valid_orders = [
            'created_at', '-created_at', 'updated_at', '-updated_at'
        ]
        if order_by in valid_orders:
            queryset = queryset.order_by(order_by)
        else:
            queryset = queryset.order_by('-created_at')

        return queryset

    def get_serializer_class(self):
        """
        Return appropriate serializer class.
        """
        if self.action == 'retrieve':
            return serializers.DocumentDetailSerializer

        return self.serializer_class
