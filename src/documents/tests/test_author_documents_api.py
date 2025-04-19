"""
Test the save documents API.
"""

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Document


AUTHORED_DOCUMENTS_URL = reverse('documents:authored-document-list-documents')


def add_authored_document_url(document_id):
    """
    Return add authored document URL.
    """
    return reverse(
        'documents:authored-document-add-document',
        args=[document_id]
    )


def delete_authored_document_url(document_id):
    """
    Return delete authored document URL.
    """
    return reverse(
        'documents:authored-document-delete-document',
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


class NonAuthorDocumentApiTests(TestCase):
    """
    Test the save document API (Authenticated as author).
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
            'last_name': 'Maternal',
        })

        self.client.force_authenticate(user=self.normal_user)

    def test_list_authored_documents(self):
        """
        Test listing authored documents fails for non-authors.
        """
        url = AUTHORED_DOCUMENTS_URL

        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_add_authored_document_fails(self):
        """
        Test adding a document to the authored documents list
        fails for non-authors.
        """
        url = add_authored_document_url(self.document.id)

        res = self.client.post(url)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AuthorDocumentApiTests(TestCase):
    """
    Test the save document API (Authenticated as author).
    """

    def setUp(self):
        self.client = APIClient()

        self.document = create_document(**{
            'title': 'Test Document',
            'repository_uri': 'https://example.com/test.pdf',
            'status': 'L'
        })

        self.author = create_user(**{
            'email': 'test@example.com',
            'password': 'testpass1234',
            'name': 'Test Name',
            'first_name': 'Parental',
            'last_name': 'Maternal',
            'is_author': True,
        })

        self.client.force_authenticate(user=self.author)

    def test_list_authored_documents_when_empty(self):
        """
        Test listing authored documents when none have been saved.
        """
        url = AUTHORED_DOCUMENTS_URL

        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 0)

    def test_author_document(self):
        """
        Test adding a document to the authored documents list.
        """
        url = add_authored_document_url(self.document.id)

        res = self.client.post(url)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        self.assertIn('message', res.data)
        self.assertIn('data', res.data)
        self.assertEqual(res.data['message'], 'Document added successfully')
        self.assertEqual(res.data['data']['document']['id'], self.document.id)

    def test_save_document_already_authored(self):
        """
        Test saving a document that is already authored.
        """
        url = add_authored_document_url(self.document.id)

        self.client.post(url)

        res = self.client.post(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('detail', res.data)
        self.assertEqual(res.data['detail'], 'Document already added')

    def test_list_authored_documents(self):
        """
        Test listing authored documents.
        """
        url = add_authored_document_url(self.document.id)

        self.client.post(url)

        res = self.client.get(AUTHORED_DOCUMENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['document']['id'], self.document.id)

    def test_unauthor_document(self):
        """
        Test removing a document from the authored documents list.
        """

        save_url = add_authored_document_url(self.document.id)
        unsave_url = delete_authored_document_url(self.document.id)

        self.client.post(save_url)
        res = self.client.delete(unsave_url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertIn('message', res.data)
        self.assertEqual(res.data['message'], 'Document removed successfully')

        list_res = self.client.get(AUTHORED_DOCUMENTS_URL)
        self.assertEqual(len(list_res.data), 0)
