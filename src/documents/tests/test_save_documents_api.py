"""
Test the save documents API.
"""

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Document


SAVED_DOCUMENTS_URL = reverse('documents:saved-document-list-documents')


def add_saved_document_url(document_id):
    """
    Return add saved document URL.
    """
    return reverse(
        'documents:saved-document-add-document',
        args=[document_id]
    )


def delete_saved_document_url(document_id):
    """
    Return delete saved document URL.
    """
    return reverse(
        'documents:saved-document-delete-document',
        args=[document_id]
    )


def create_user(**params):
    """
    Helper function to create a user.
    """
    return get_user_model().objects.create_user(**params)


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


class SaveDocumentApiTests(TestCase):
    """
    Test the save document API (Authenticated).
    """

    def setUp(self):
        self.client = APIClient()

        self.document = create_document(**{
            'title': 'Test Document',
            'repository_uri': 'https://example.com/test.pdf',
            'status': 'L'
        })

        self.normal_user = create_user(**{
            'email': 'test@example.com',
            'password': 'testpass1234',
            'name': 'Test Name',
            'first_name': 'Parental',
            'last_name': 'Maternal'
        })

        self.client.force_authenticate(user=self.normal_user)

    def test_list_saved_documents_when_empty(self):
        """
        Test listing saved documents when
        none have been saved.
        """
        url = SAVED_DOCUMENTS_URL

        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 0)

    def test_save_document(self):
        """
        Test saving a document.
        """
        url = add_saved_document_url(self.document.id)

        res = self.client.post(url)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        self.assertIn('message', res.data)
        self.assertIn('data', res.data)
        self.assertEqual(res.data['message'], 'Document added successfully')
        self.assertEqual(res.data['data']['document']['id'], self.document.id)

    def test_save_document_already_saved(self):
        """
        Test saving a document that is already saved.
        """
        url = add_saved_document_url(self.document.id)

        self.client.post(url)

        res = self.client.post(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('error', res.data)
        self.assertEqual(res.data['error'], 'Document already added')

    def test_list_saved_documents(self):
        """
        Test listing saved documents.
        """
        url = add_saved_document_url(self.document.id)

        self.client.post(url)

        res = self.client.get(SAVED_DOCUMENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['document']['id'], self.document.id)

    def test_unsave_document(self):
        """
        Test unsaving a document.
        """

        save_url = add_saved_document_url(self.document.id)
        unsave_url = delete_saved_document_url(self.document.id)

        self.client.post(save_url)
        res = self.client.delete(unsave_url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertIn('message', res.data)
        self.assertEqual(res.data['message'], 'Document removed successfully')

        list_res = self.client.get(SAVED_DOCUMENTS_URL)
        self.assertEqual(len(list_res.data), 0)
