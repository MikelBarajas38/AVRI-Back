"""
Test the RAGFlowService class
"""

import os
from unittest import TestCase
from unittest.mock import patch, Mock
import requests

from core.services.ragflow_service import RAGFlowService


class TestRAGFlowService(TestCase):
    """
    Test RAGFlowService methods
    """

    def setUp(self):
        """
        Set up test fixtures
        """
        # Set environment variables for testing
        os.environ['RAGFLOW_BASE_URL'] = 'http://test-ragflow.com/api'
        os.environ['RAGFLOW_API_KEY'] = 'test-api-key'
        os.environ['DATASET_ID'] = 'test-dataset-id'

        self.service = RAGFlowService()

    def tearDown(self):
        """
        Clean up after tests
        """
        if 'RAGFLOW_BASE_URL' in os.environ:
            del os.environ['RAGFLOW_BASE_URL']
        if 'RAGFLOW_API_KEY' in os.environ:
            del os.environ['RAGFLOW_API_KEY']
        if 'DATASET_ID' in os.environ:
            del os.environ['DATASET_ID']

    def test_initialization_from_env(self):
        """
        Test that RAGFlowService initializes correctly
        """
        service = RAGFlowService()

        self.assertEqual(service.base_url, 'http://test-ragflow.com/api')
        self.assertEqual(service.api_key, 'test-api-key')
        self.assertEqual(
            service.headers['Authorization'],
            'Bearer test-api-key'
        )
        self.assertEqual(service.headers['Content-Type'], 'application/json')

    def test_initialization_with_params(self):
        """
        Test that RAGFlowService can be initialized with explicit parameters
        """
        service = RAGFlowService(
            base_url='http://custom-url.com',
            api_key='custom-key'
        )

        self.assertEqual(service.base_url, 'http://custom-url.com')
        self.assertEqual(service.api_key, 'custom-key')
        self.assertEqual(service.headers['Authorization'], 'Bearer custom-key')

    def test_initialization_without_api_key(self):
        """
        Test initialization when no API key is provided
        """
        # Remove API key from environment
        if 'RAGFLOW_API_KEY' in os.environ:
            del os.environ['RAGFLOW_API_KEY']

        service = RAGFlowService()

        self.assertIsNone(service.api_key)
        self.assertIsNone(service.headers['Authorization'])

    @patch('requests.get')
    def test_list_assistants_all(self, mock_get):
        """
        Test listing all assistants without name filter
        """

        mock_response = Mock()
        mock_response.json.return_value = {
            'code': 0,
            'data': [
                {'id': 'assistant-1', 'name': 'Assistant One'},
                {'id': 'assistant-2', 'name': 'Assistant Two'}
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        result = self.service.list_assistants()

        mock_get.assert_called_once_with(
            'http://test-ragflow.com/api/chats',
            headers=self.service.headers,
            params={}
        )

        self.assertEqual(result['code'], 0)
        self.assertEqual(len(result['data']), 2)
        self.assertEqual(result['data'][0]['name'], 'Assistant One')

    @patch('requests.get')
    def test_list_assistants_with_name(self, mock_get):
        """
        Test listing assistants with name filter
        """
        mock_response = Mock()
        mock_response.json.return_value = {
            'code': 0,
            'data': [{'id': 'assistant-1', 'name': 'AVRI'}]
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        result = self.service.list_assistants(name='AVRI')

        mock_get.assert_called_once_with(
            'http://test-ragflow.com/api/chats',
            headers=self.service.headers,
            params={'name': 'AVRI'}
        )

        self.assertEqual(result['data'][0]['name'], 'AVRI')

    @patch('requests.get')
    def test_list_assistants_error(self, mock_get):
        """
        Test list_assistants handles HTTP errors
        """
        mock_get.side_effect = requests.HTTPError('404 Not Found')

        with self.assertRaises(requests.HTTPError):
            self.service.list_assistants()

    @patch('requests.get')
    def test_list_sessions_all(self, mock_get):
        """
        Test listing all sessions for an assistant
        """
        mock_response = Mock()
        mock_response.json.return_value = {
            'code': 0,
            'data': [
                {'id': 'session-1', 'name': 'Session One'},
                {'id': 'session-2', 'name': 'Session Two'}
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        result = self.service.list_sessions(assistant_id='assistant-1')

        mock_get.assert_called_once_with(
            'http://test-ragflow.com/api/chats/assistant-1/sessions',
            headers=self.service.headers,
            params={}
        )

        self.assertEqual(len(result['data']), 2)

    @patch('requests.get')
    def test_list_sessions_with_id(self, mock_get):
        """
        Test listing a specific session by ID
        """
        mock_response = Mock()
        mock_response.json.return_value = {
            'code': 0,
            'data': [
                {'role': 'user', 'content': 'Hello'},
                {'role': 'assistant', 'content': 'Hi there!'}
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        result = self.service.list_sessions(
            assistant_id='assistant-1',
            session_id='session-1'
        )

        mock_get.assert_called_once_with(
            'http://test-ragflow.com/api/chats/assistant-1/sessions',
            headers=self.service.headers,
            params={'id': 'session-1'}
        )

        self.assertEqual(result['data'][0]['role'], 'user')

    @patch('requests.post')
    def test_create_session_without_id(self, mock_post):
        """
        Test creating a new session without specifying ID
        """
        mock_response = Mock()
        mock_response.json.return_value = {
            'code': 0,
            'data': {'id': 'new-session-id', 'name': 'My Session'}
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        result = self.service.create_session(
            assistant_id='assistant-1',
            session_name='My Session'
        )

        mock_post.assert_called_once_with(
            'http://test-ragflow.com/api/chats/assistant-1/sessions',
            headers=self.service.headers,
            params={},
            json={'name': 'My Session'}
        )

        self.assertEqual(result['data']['id'], 'new-session-id')

    @patch('requests.post')
    def test_create_session_with_id(self, mock_post):
        """
        Test creating a session with a specific ID
        """
        mock_response = Mock()
        mock_response.json.return_value = {
            'code': 0,
            'data': {'id': 'custom-id', 'name': 'My Session'}
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        self.service.create_session(
            assistant_id='assistant-1',
            session_name='My Session',
            session_id='custom-id'
        )

        mock_post.assert_called_once_with(
            'http://test-ragflow.com/api/chats/assistant-1/sessions',
            headers=self.service.headers,
            params={'id': 'custom-id'},
            json={'name': 'My Session'}
        )

    @patch('requests.delete')
    def test_delete_session(self, mock_delete):
        """
        Test deleting sessions
        """
        mock_response = Mock()
        mock_response.json.return_value = {
            'code': 0,
            'message': 'Sessions deleted successfully'
        }
        mock_response.raise_for_status = Mock()
        mock_delete.return_value = mock_response

        result = self.service.delete_session(
            assistant_id='assistant-1',
            session_ids=['session-1', 'session-2']
        )

        mock_delete.assert_called_once_with(
            'http://test-ragflow.com/api/chats/assistant-1/sessions/',
            headers=self.service.headers,
            json={'ids': ['session-1', 'session-2']}
        )

        self.assertEqual(result['code'], 0)

    @patch('requests.post')
    def test_ask_with_session_id(self, mock_post):
        """
        Test asking a question with session ID
        """
        mock_response = Mock()
        mock_response.json.return_value = {
            'code': 0,
            'data': {
                'answer': 'This is the answer',
                'reference': []
            }
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        result = self.service.ask(
            assistant_id='assistant-1',
            question='What is the answer?',
            session_id='session-1'
        )

        mock_post.assert_called_once_with(
            'http://test-ragflow.com/api/chats/assistant-1/completions',
            headers=self.service.headers,
            json={
                'question': 'What is the answer?',
                'stream': False,
                'session_id': 'session-1'
            }
        )

        self.assertEqual(result['data']['answer'], 'This is the answer')

    @patch('requests.post')
    def test_ask_with_user_id(self, mock_post):
        """
        Test asking a question with user ID instead of session ID
        """
        mock_response = Mock()
        mock_response.json.return_value = {
            'code': 0,
            'data': {'answer': 'Answer for user'}
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        self.service.ask(
            assistant_id='assistant-1',
            question='Question from user',
            user_id='user-123'
        )

        mock_post.assert_called_once_with(
            'http://test-ragflow.com/api/chats/assistant-1/completions',
            headers=self.service.headers,
            json={
                'question': 'Question from user',
                'stream': False,
                'user_id': 'user-123'
            }
        )

    @patch('requests.post')
    def test_ask_with_stream(self, mock_post):
        """
        Test asking with stream enabled
        """
        mock_response = Mock()
        mock_response.json.return_value = {
            'code': 0,
            'data': {'answer': 'Streamed answer'}
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        self.service.ask(
            assistant_id='assistant-1',
            question='Stream this',
            stream=True,
            session_id='session-1'
        )

        expected_body = {
            'question': 'Stream this',
            'stream': True,
            'session_id': 'session-1'
        }

        mock_post.assert_called_once()
        actual_body = mock_post.call_args[1]['json']
        self.assertEqual(actual_body, expected_body)

    @patch('requests.post')
    def test_get_chunks(self, mock_post):
        """
        Test getting chunks for retrieval
        """
        mock_response = Mock()
        mock_response.json.return_value = {
            'code': 0,
            'data': {
                'chunks': [
                    {'document_id': 'doc1', 'content': 'Content 1'},
                    {'document_id': 'doc2', 'content': 'Content 2'}
                ]
            }
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        result = self.service.get_chunks(query='machine learning')

        mock_post.assert_called_once()

        actual_call = mock_post.call_args
        self.assertEqual(
            actual_call[0][0],
            'http://test-ragflow.com/api/retrieval'
        )

        actual_json = actual_call[1]['json']
        self.assertEqual(actual_json['question'], 'machine learning')
        self.assertIn('dataset_ids', actual_json)

        self.assertEqual(len(result['data']['chunks']), 2)

    @patch('requests.post')
    def test_get_chunks_with_custom_datasets(self, mock_post):
        """
        Test getting chunks with custom dataset IDs
        """
        mock_response = Mock()
        mock_response.json.return_value = {
            'code': 0,
            'data': {'chunks': []}
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        self.service.get_chunks(
            query='test query',
            dataset_ids=['dataset-1', 'dataset-2']
        )

        mock_post.assert_called_once_with(
            'http://test-ragflow.com/api/retrieval',
            headers=self.service.headers,
            json={
                'question': 'test query',
                'dataset_ids': ['dataset-1', 'dataset-2']
            }
        )

    @patch('requests.post')
    def test_get_chunks_error_handling(self, mock_post):
        """
        Test get_chunks handles errors properly
        """
        mock_post.side_effect = requests.HTTPError('500 Server Error')

        with self.assertRaises(requests.HTTPError):
            self.service.get_chunks(query='test')
