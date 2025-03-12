"""
Tests for the documents API.
"""

from django.test import TestCase
from django.urls import reverse

# from rest_framework import status
from rest_framework.test import APIClient

from core.models import Document

"""
from documents.serializers import (
    DocumentSerializer,
    DocumentDetailSerializer
)
"""


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
    Test the documents API (public).
    """

    def setUp(self):
        self.client = APIClient()

    def test_get_documents(self):
        """
        Test retrieving a list of documents.
        """
        return

    def test_get_documents_ordered_by_created_at(self):
        """
        Test that documents are ordered by created_at (newest first).
        """
        return

    def test_get_documents_ordered_by_updated_at(self):
        """
        Test that documents are ordered by updated_at.
        """
        return

    def test_get_document_detail(self):
        """
        Test getting a document detail.
        """
        return
