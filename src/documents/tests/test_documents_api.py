"""
Tests for the documents API.
"""

from datetime import datetime, timedelta

from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Document

from documents.serializers import (
    DocumentSerializer,
    DocumentDetailSerializer
)


DOCUMENTS_URL = reverse('documents:document-list')


def detail_url(document_id):
    """
    Return document detail URL.
    """
    return reverse('documents:document-detail', args=[document_id])


def create_document(**params):
    """
    Helper function to create a sample document.
    """
    defaults = {
        'title': 'Test document',
        'repository_uri': 'https://example.com',
        'status': 'L',
    }
    defaults.update(params)
    document = Document.objects.create(**defaults)
    return document


class PublicDocumentsApiTests(TestCase):
    """
    Test the public documents API (Unauthenticated).
    """

    def setUp(self):
        """
        Create sample documents for testing ordering.
        """
        self.client = APIClient()

    def test_get_documents(self):
        """
        Test retrieving a list of documents.
        """
        create_document(**{'title': 'Document 1'})
        create_document(**{'title': 'Document 2'})

        res = self.client.get(DOCUMENTS_URL)

        documents = Document.objects.all().order_by('-created_at')

        serializer = DocumentSerializer(documents, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_documents_ordered_by_created_at(self):
        """
        Test that documents are ordered by created_at (newest first).
        """
        now = datetime.now()

        create_document(**{
            'title': 'Document 1',
            'created_at': now - timedelta(days=1),
            'updated_at': now - timedelta(days=3)
        })

        create_document(**{
            'title': 'Document 2',
            'created_at': now - timedelta(days=2),
            'updated_at': now - timedelta(days=2)
        })

        create_document(**{
            'title': 'Document 3',
            'created_at': now - timedelta(days=3),
            'updated_at': now - timedelta(days=1)
        })

        res = self.client.get(DOCUMENTS_URL, {'ordering': '-created_at'})

        documents = Document.objects.all().order_by('-created_at')

        serializer = DocumentSerializer(documents, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_documents_ordered_by_updated_at(self):
        """
        Test that documents are ordered by updated_at.
        """
        now = datetime.now()

        create_document(**{
            'title': 'Document 1',
            'created_at': now - timedelta(days=1),
            'updated_at': now - timedelta(days=3)
        })

        create_document(**{
            'title': 'Document 2',
            'created_at': now - timedelta(days=2),
            'updated_at': now - timedelta(days=2)
        })

        create_document(**{
            'title': 'Document 3',
            'created_at': now - timedelta(days=3),
            'updated_at': now - timedelta(days=1)
        })

        res = self.client.get(DOCUMENTS_URL, {'ordering': '-updated_at'})

        documents = Document.objects.all().order_by('-updated_at')

        serializer = DocumentSerializer(documents, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_document_detail(self):
        """
        Test getting a document detail.
        """
        document = create_document()

        url = detail_url(document.id)
        res = self.client.get(url)

        serializer = DocumentDetailSerializer(document)

        self.assertEqual(res.data, serializer.data)
