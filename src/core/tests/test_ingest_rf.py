"""
Test custom Django management commands for ingest_rf.
"""

import os
import tempfile
from functools import wraps
from io import StringIO
from unittest.mock import AsyncMock, Mock, patch

from django.core.management import CommandError, call_command
from django.test import TestCase

from core.management.commands.ingest_rf import Command as IngestCommand


def silence_ingest_output(test_method):
    """
    Decorator to silence ingest_rf command output in tests.
    """

    @wraps(test_method)
    def wrapper(*args, **kwargs):
        with patch("sys.stdout", new_callable=StringIO):
            return test_method(*args, **kwargs)

    return wrapper


class IngestRFCommandTests(TestCase):
    """
    Test the ingest_rf management command.
    """

    def setUp(self) -> None:
        """
        Set up test fixtures
        """
        # Set up environment variables required by the command
        os.environ["RI_BASE_URL"] = "http://test-ri.com"
        os.environ["RI_BASE_URL_REST"] = "http://test-ri-rest.com"
        os.environ["RAGFLOW_API_KEY"] = "test-api-key"
        os.environ["RAGFLOW_BASE_URL"] = "http://test-ragflow.com/api"
        os.environ["DATASET_ID"] = "test-dataset-id"

        # create temporary directory for test files
        self.test_folder = tempfile.mkdtemp()

        # Mock common objects
        self.mock_dataset = Mock()
        self.mock_dataset.id = "test-dataset-id"
        self.mock_dataset.name = "Test DataSet"

    def tearDown(self) -> None:
        """
        Clean up after tests.
        """
        # Remove environment variables
        for env_var in [
            "RI_BASE_URL",
            "RI_BASE_URL_REST",
            "RAGFLOW_API_KEY",
            "RAGFLOW_BASE_URL",
            "DATASET_ID",
        ]:
            if env_var in os.environ:
                del os.environ[env_var]

        # clean up temporary directory
        import shutil

        shutil.rmtree(self.test_folder, ignore_errors=True)

    @silence_ingest_output
    def test_missing_environment_variables(self):
        """
        Test that command fails when required environment
        variables are missing.
        """
        # Test missing RI_BASE_URL
        with patch.dict(os.environ, {"RI_BASE_URL": ""}):
            with self.assertRaises(CommandError) as context:
                call_command("ingest_rf")
            self.assertIn("RI_BASE_URL not found", str(context.exception))

        # Test missing RI_BASE_URL_REST
        with patch.dict(os.environ, {"RI_BASE_URL_REST": ""}):
            with self.assertRaises(CommandError) as context:
                call_command("ingest_rf")
            self.assertIn("RI_BASE_URL_REST not found", str(context.exception))

        # Test missing RAGFLOW_API_KEY
        with patch.dict(os.environ, {"RAGFLOW_API_KEY": ""}):
            with self.assertRaises(CommandError) as context:
                call_command("ingest_rf")
            self.assertIn("RAGFLOW_API_KEY not found", str(context.exception))

        # Test missing RAGFLOW_BASE_URL
        with patch.dict(os.environ, {"RAGFLOW_BASE_URL": ""}):
            with self.assertRaises(CommandError) as context:
                call_command("ingest_rf")
            self.assertIn("RAGFLOW_BASE_URL not found", str(context.exception))

        # Test missing DATASET_ID
        with patch.dict(os.environ, {"DATASET_ID": ""}):
            with self.assertRaises(CommandError) as context:
                call_command("ingest_rf")
            self.assertIn("DATASET_ID not found", str(context.exception))

    @patch.object(IngestCommand, "_get_dataset")
    @patch.object(IngestCommand, "_get_existing_repository_uuids")
    @patch("core.management.commands.ingest_rf.RAGFlow")
    @silence_ingest_output
    def test_successful_initialization(
        self,
        mock_ragflow_class,
        mock_get_uuids,
        mock_get_dataset,
    ):
        """
        Test successful command intialization with all dependencies.
        """
        # Mock dependencies
        mock_ragflow_instance = Mock()
        mock_ragflow_class.return_value = mock_ragflow_instance

        mock_get_uuids.return_value = set()
        mock_get_dataset.return_value = self.mock_dataset

        # Mock the parallel processing to return empty
        # result (no  new documents)
        with patch(
            "core.management.commands.ingest_rf.process_items_in_parallel"
        ) as mock_process:
            mock_process.return_value = {}

            # Mock asyncio.run for monitoring
            with patch("asyncio.run"):
                try:
                    call_command("ingest_rf", folder_path=self.test_folder)
                    # If we get here, command executed without errors
                    self.assertTrue(True)
                except CommandError:
                    self.fail("Command raised CommandError unexpectedly")

    @patch.object(IngestCommand, "_get_dataset")
    @patch.object(IngestCommand, "_get_existing_repository_uuids")
    @patch.object(IngestCommand, "_create_documents")
    @patch.object(IngestCommand, "_remove_temp_pdf")
    @patch(
        "core.management.commands.ingest_rf.monitor_parsing",
        new_callable=AsyncMock,
    )
    @patch("core.management.commands.ingest_rf.RAGFlow")
    @silence_ingest_output
    def test_document_processing_flow(
        self,
        mock_ragflow_class,
        mock_monitor_parsing,
        mock_remove_pdf,
        mock_create_docs,
        mock_get_uuids,
        mock_get_dataset,
    ):
        """
        Test the complete document processing flow with mock data
        """
        # Mock dependencies
        mock_ragflow_instance = Mock()
        mock_ragflow_class.return_value = mock_ragflow_instance
        mock_get_uuids.return_value = set()
        mock_get_dataset.return_value = self.mock_dataset

        # Mock document data
        test_document_ids = ["doc-1", "doc-2"]
        test_metadata_map = {
            "doc-1": {
                "name": "Test Document 1",
                "uuid": "uuid-1",
                "handle": "12345",
                "metadata": {"dc.rights": "open"},
                "bitstreams": [{"name": "doc1.pdf"}],
                "inArchive": True,
                "discoverable": True,
                "withdrawn": False,
            },
            "doc-2": {
                "name": "Test Document 2",
                "uuid": "uuid-2",
                "handle": "67890",
                "metadata": {"dc.rights": "restricted"},
                "bitstreams": [{"name": "doc2.pdf"}],
                "inArchive": True,
                "discoverable": False,
                "withdrawn": False,
            },
        }

        # Mock the parallel processing to return our test data
        with patch(
            "core.management.commands.ingest_rf.process_items_in_parallel"
        ) as mock_process:
            # Make process_items_in_parallel modify document_ids
            def side_effect(**kwargs):
                document_ids_arg = kwargs.get("document_ids", [])
                if document_ids_arg is not None:
                    document_ids_arg.extend(test_document_ids)
                return test_metadata_map

            mock_process.side_effect = side_effect

            # Mock dataset.list_documents to return done status
            mock_doc1 = Mock()
            mock_doc1.id = "doc-1"
            mock_doc1.run = "DONE"
            mock_doc2 = Mock()
            mock_doc2.id = "doc-2"
            mock_doc2.run = "DONE"
            self.mock_dataset.list_documents.return_value = [
                mock_doc1,
                mock_doc2,
            ]

            # Call command with limit items
            call_command("ingest_rf", li=2, folder_path=self.test_folder)

            # Verify document creation was called
            mock_create_docs.assert_called_once()

            # Verify monitoring was called (if applicable)
            if mock_monitor_parsing.called:
                mock_monitor_parsing.assert_called()

            # Verify PDF removal was called with correct file names
            mock_remove_pdf.assert_called_once()
            call_args = mock_remove_pdf.call_args[1]
            self.assertEqual(call_args["folder_path"], self.test_folder)
            self.assertIn("doc1.pdf", call_args["processed_file_names"])
            self.assertIn("doc2.pdf", call_args["processed_file_names"])

    @patch.object(IngestCommand, "_get_dataset")
    @patch.object(IngestCommand, "_get_existing_repository_uuids")
    @patch("core.management.commands.ingest_rf.RAGFlow")
    @silence_ingest_output
    def test_no_new_documents(
        self, mock_ragflow_class, mock_get_uuids, mock_get_dataset
    ):
        """
        Test when no new documents are found to ingest.
        """
        # Mock dependencies
        mock_ragflow_instance = Mock()
        mock_ragflow_class.return_value = mock_ragflow_instance
        mock_get_uuids.return_value = {"existing_uuids-1", "existing_uuids-2"}
        mock_get_dataset.return_value = self.mock_dataset

        # Mock empty results from processing (all documents already exist)
        with patch(
            "core.management.commands.ingest_rf.process_items_in_parallel"
        ) as mock_process:
            mock_process.return_value = {}

            with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
                call_command("ingest_rf", folder_path=self.test_folder)

                output = mock_stdout.getvalue()
                self.assertIn("No new documents to ingest", output)

    def test_determine_document_status(self):
        """
        Test the _determine_document_status helper method.
        """

        from core.management.commands.ingest_rf import Command

        command = Command()

        # Test open acces
        metadata_open = {
            "metadata": {"dc.rights": "open access"},
            "inArchive": True,
            "discoverable": True,
            "withdrawn": False,
        }
        status = command._determine_document_status(metadata_open)
        self.assertEqual(status, "L")

        # Test restricted
        metadata_restricted = {
            "metadata": {"dc.rights": "restricted"},
            "inArchive": True,
            "discoverable": False,
            "withdrawn": False,
        }
        status = command._determine_document_status(metadata_restricted)
        self.assertEqual(status, "R")

        # Test embargo
        metadata_embargo = {
            "metadata": {"dc.rights": "embargoed"},
            "inArchive": False,
            "discoverable": False,
            "withdrawn": False,
        }
        status = command._determine_document_status(metadata_embargo)
        self.assertEqual(status, "E")

        @patch("core.models.Document.objects.update_or_create")
        def test_create_documents(self, mock_update_or_create):
            """
            Test the _create_documents method.
            """
            from core.management.commands.ingest_rf import Command

            command = Command()

            test_metadata_map = {
                "ragflow-1": {
                    "name": "Test Doc",
                    "uuid": "test-uuid",
                    "handle": "12345",
                    "metadata": {"dc.rights": "open"},
                    "inArchive": True,
                    "discoverable": True,
                    "withdrawn": False,
                }
            }

            # Mock successful document creation
            mock_update_or_create.return_value = (
                Mock(),
                True,
            )  # (instance, created)

            with patch("sys.stdout", new_callable=StringIO):
                command._create_documents(test_metadata_map)

            # Verify document was created with correct parameters
            mock_update_or_create.assert_called_once()

    @patch("core.management.commands.ingest_rf.RAGFlow")
    @patch.object(IngestCommand, "_get_dataset")
    @patch.object(IngestCommand, "_get_existing_repository_uuids")
    @silence_ingest_output
    def test_ragflow_initialization_error(
        self, mock_get_uuids, mock_get_dataset, mock_ragflow_class
    ):
        """
        Test handling of RAGFlow initialization errors.
        """
        # Mock RAGFlow initialization failure
        mock_ragflow_class.side_effect = Exception("Connection failed")

        with self.assertRaises(CommandError) as context:
            call_command("ingest_rf", folder_path=self.test_folder)

        self.assertIn("Failed to initialize RAGFlow", str(context.exception))

    @patch.object(IngestCommand, "_get_dataset")
    @patch.object(IngestCommand, "_get_existing_repository_uuids")
    @patch("core.management.commands.ingest_rf.RAGFlow")
    @silence_ingest_output
    def test_dataset_not_found(
        self, mock_ragflow_class, mock_get_uuids, mock_get_dataset
    ):
        """
        Test handling when dataset is not found.
        """
        # Mock dependencies
        mock_ragflow_instance = Mock()
        mock_ragflow_class.return_value = mock_ragflow_instance
        mock_get_uuids.return_value = set()
        mock_get_dataset.return_value = None  # Datset not found

        with self.assertRaises(CommandError) as context:
            call_command("ingest_rf", folder_path=self.test_folder)

        self.assertIn("Dataset", str(context.exception))

    @patch.object(IngestCommand, "_get_dataset")
    @patch.object(IngestCommand, "_get_existing_repository_uuids")
    @patch("core.management.commands.ingest_rf.RAGFlow")
    @silence_ingest_output
    def test_command_arguments(
        self, mock_ragflow_class, mock_get_uuids, mock_get_dataset
    ):
        """
        Test that command arguments are properly handled.
        """

        # Mock dependencies
        mock_ragflow_instance = Mock()
        mock_ragflow_class.return_value = mock_ragflow_instance
        mock_get_uuids.return_value = set()
        mock_get_dataset.return_value = self.mock_dataset

        with patch(
            "core.management.commands.ingest_rf.process_items_in_parallel"
        ) as mock_process:
            mock_process.return_value = {}
            with patch("asyncio.run"):
                # Test with custom arguments
                call_command(
                    "ingest_rf",
                    li=5,
                    folder_path=self.test_folder,
                    max_tasks=10,
                    poll_interval=1.0,
                )

                # Verify process_items_in_parallel was
                # called with correct arguments
                mock_process.assert_called_once()
                call_args = mock_process.call_args[1]
                self.assertEqual(call_args["limit_items"], 5)
                self.assertEqual(call_args["max_concurrent_tasks"], 10)
                self.assertEqual(call_args["folder_path"], self.test_folder)

    @patch("core.models.Document.objects.update_or_create")
    @patch.dict(os.environ, {"RI_BASE_URL": "http://test-ri.com"})
    @silence_ingest_output
    def test_create_documents_success(self, mock_update_or_create):
        """
        Test _create_documents with successful document creation.
        """
        command = IngestCommand()
        command.stdout = Mock()
        command.stderr = Mock()

        metadata_map = {
            "ragflow-1": {
                "name": "Test Document 1",
                "uuid": "uuid-1",
                "handle": "12345",
                "metadata": {"dc.rights": "open"},
                "inArchive": True,
                "discoverable": True,
                "withdrawn": False,
            },
            "ragflow-2": {
                "name": "Test Document 2",
                "uuid": "uuid-2",
                "handle": "",
                "metadata": {"dc.rights": "restricted"},
                "inArchive": True,
                "discoverable": False,
                "withdrawn": False,
            },
        }

        # Mock first call returns created=True, second returns created=False
        mock_update_or_create.side_effect = [
            (Mock(), True),  # First document created
            (Mock(), False),  # Second document updated
        ]

        command._create_documents(metadata_map)

        # Verify update_or_create was called twice
        self.assertEqual(mock_update_or_create.call_count, 2)

        # Verify stdout writes
        self.assertEqual(
            command.stdout.write.call_count, 3
        )  # 2 documents + summary

    @patch("core.models.Document.objects.update_or_create")
    @silence_ingest_output
    def test_create_documents_with_exception(self, mock_update_or_create):
        """
        Test _create_documents when document creation fails.
        """
        command = IngestCommand()
        command.stdout = Mock()
        command.stderr = Mock()

        metadata_map = {
            "ragflow-1": {
                "name": "Test Document",
                "uuid": "uuid-1",
                "handle": "12345",
                "metadata": {"dc.rights": "open"},
                "inArchive": True,
                "discoverable": True,
                "withdrawn": False,
            }
        }

        mock_update_or_create.side_effect = Exception("Database error")

        command._create_documents(metadata_map)

        command.stderr.write.assert_called_once()
