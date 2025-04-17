"""
Views for the documents API
"""

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.filters import OrderingFilter
from rest_framework.decorators import action
from rest_framework import authentication, permissions

from core.models import (
    Document,
    AuthoredDocument,
    SavedDocument
)

from core.permissions import IsAuthor

from documents import serializers


class DocumentViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Manage documents in the database
    """
    serializer_class = serializers.DocumentSerializer
    queryset = Document.objects.all()
    filter_backends = [OrderingFilter]
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']

    def get_queryset(self):
        """
        Return documents ordered by created_at (newest first).
        Allows ordering by updated_at if specified.
        """

        order_by = self.request.query_params.get('ordering', '-created_at')
        valid_orders = [
            'created_at', '-created_at', 'updated_at', '-updated_at'
        ]
        if order_by in valid_orders:
            queryset = self.queryset.order_by(order_by)
        else:
            queryset = self.queryset.order_by('-created_at')

        return queryset

    def get_serializer_class(self):
        """
        Return appropriate serializer class.
        """
        if self.action == 'retrieve':
            return serializers.DocumentDetailSerializer

        return self.serializer_class


class SavedDocumentViewSet(viewsets.GenericViewSet):
    """
    Manage the current user's saved documents in the database
    """
    serializer_class = serializers.SavedDocumentSerializer
    queryset = SavedDocument.objects.all()
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Return saved documents for the authenticated user.
        """
        user_queryset = self.queryset.filter(user=self.request.user)
        return user_queryset.order_by('-created_at')

    def get_serializer_class(self):
        return self.serializer_class

    @action(detail=False, methods=['get'], url_path='list')
    def list_documents(self, request):
        """
        List all saved documents for the authenticated user.
        """
        saved_documents = self.get_queryset()
        serializer = self.get_serializer(saved_documents, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
            detail=False,
            methods=['post'],
            url_path='add/(?P<document_id>[^/.]+)',
        )
    def add_document(self, request, document_id=None):
        """
        Save a document for the authenticated user.
        """
        try:
            document = Document.objects.get(id=document_id)
        except Document.DoesNotExist:
            return Response(
                {'error': 'Document not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        saved_document, created = SavedDocument.objects.get_or_create(
            user=self.request.user,
            document=document
        )

        serializer = self.get_serializer(saved_document)
        data = serializer.data

        if created:
            return Response(
                {
                    'message': 'Document added successfully',
                    'data': data
                },
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                {'error': 'Document already added'},
                status=status.HTTP_200_OK
            )

    @action(
            detail=False,
            methods=['delete'],
            url_path='delete/(?P<document_id>[^/.]+)'
    )
    def delete_document(self, request, document_id=None):
        """
        Unsave a document for the authenticated user.
        """
        try:
            saved_document = SavedDocument.objects.get(
                user=self.request.user,
                document__id=document_id
            )
            saved_document.delete()
            return Response(
                {'message': 'Document removed successfully'},
                status=status.HTTP_204_NO_CONTENT
            )
        except SavedDocument.DoesNotExist:
            return Response(
                {'error': 'Saved document not found'},
                status=status.HTTP_404_NOT_FOUND
            )


class AuthoredDocumentViewSet(viewsets.GenericViewSet):
    """
    Manage the current user's authored documents in the database
    """
    serializer_class = serializers.AuthoredDocumentSerializer
    queryset = AuthoredDocument.objects.all()
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated, IsAuthor]

    def get_queryset(self):
        """
        Return authored documents for the authenticated user.
        """
        user_queryset = self.queryset.filter(author=self.request.user)
        return user_queryset.order_by('-created_at')

    def get_serializer_class(self):
        return self.serializer_class

    @action(detail=False, methods=['get'], url_path='list')
    def list_documents(self, request):
        """
        List all of the user's authored documents.
        """
        authored_documents = self.get_queryset()
        serializer = self.get_serializer(authored_documents, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
            detail=False,
            methods=['post'],
            url_path='add/(?P<document_id>[^/.]+)',
        )
    def add_document(self, request, document_id=None):
        """
        Add a document as authored by the authenticated user.
        """
        try:
            document = Document.objects.get(id=document_id)
        except Document.DoesNotExist:
            return Response(
                {'error': 'Document not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        authored_document, created = AuthoredDocument.objects.get_or_create(
            author=self.request.user,
            document=document
        )

        serializers = self.get_serializer(authored_document)
        data = serializers.data

        if created:
            return Response(
                {
                    'message': 'Document added successfully',
                    'data': data
                },
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                {'error': 'Document already added'},
                status=status.HTTP_200_OK
            )

    @action(
            detail=False,
            methods=['delete'],
            url_path='delete/(?P<document_id>[^/.]+)'
        )
    def delete_document(self, request, document_id=None):
        """
        Remove a document from the user's authored documents.
        """
        try:
            authored_document = AuthoredDocument.objects.get(
                author=self.request.user,
                document__id=document_id
            )
            authored_document.delete()
            return Response(
                {'message': 'Document removed successfully'},
                status=status.HTTP_204_NO_CONTENT
            )
        except AuthoredDocument.DoesNotExist:
            return Response(
                {'error': 'Authored document not found'},
                status=status.HTTP_404_NOT_FOUND
            )
