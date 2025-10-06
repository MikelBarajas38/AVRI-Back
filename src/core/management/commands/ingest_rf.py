"""
Django command to run the ingest pipeline from RI to Rag Flow.
"""

import asyncio
import os
from typing import Optional

from django.core.management.base import BaseCommand, CommandError
from ingest_ragflow.rag.parsing import (
    monitor_parsing,
    process_items_in_parallel,
)
from ragflow_sdk import RAGFlow
from ragflow_sdk.modules.dataset import DataSet
from tqdm import tqdm


class Command(BaseCommand):
    help = "Run the ingest pipeline from RI to RAG Flow"

    def add_arguments(self, parser):
        parser.add_argument(
            "--li",
            required=False,
            default=None,
            type=int,
            help="Total number of retrieve items",
        )
        parser.add_argument(
            "folder_path",
            required=False,
            default="ingest_tmp",
            type=str,
            help="Folder path for downloaded files",
        )
        parser.add_argument(
            "--max_tasks",
            required=False,
            default=4,
            type=int,
            help="Maximum number of concurrent",
        )
        parser.add_argument(
            "--poll_interval",
            required=False,
            default=2.5,
            type=float,
            help="Interval (in seconds) between \
            status checks",
        )

    def handle(self, *args, **options):
        try:
            # Configuration from environment variables
            RI_BASE_URL = os.getenv("RI_BASE_URL")
            RI_BASE_URL_REST = os.getenv("RI_BASE_URL_REST")
            API_KEY = os.getenv("RAGFLOW_API_KEY")
            RAGFLOW_URL = os.getenv("RAGFLOW_BASE_URL")
            DATASET_ID = os.getenv("DATASET_ID")
            # Set up parameters
            LIMIT_ITEMS = options["li"]
            MAX_CONCURRENT_TASKS = options["max_tasks"]
            POLL_INTERVAL = options["poll_interval"]
            FOLDER_PATH = options["folder_path"]

            # Validate environment variables
            if not RI_BASE_URL:
                raise CommandError("RI_BASE_URL not found in settings")
            if not RI_BASE_URL_REST:
                raise CommandError("RI_BASE_URL_REST not found in settings")
            if not API_KEY:
                raise CommandError("RAGFLOW_API_KEY not found in settings")
            if not RAGFLOW_URL:
                raise CommandError("RAGFLOW_BASE_URL not found in settings")
            if not DATASET_ID:
                raise CommandError("DATASET_ID not found in settings")

            # Remove '/api/v1'
            if RAGFLOW_URL and RAGFLOW_URL.endswith("/api/v1"):
                RAGFLOW_URL = RAGFLOW_URL[:-7]

            # Create output directory if it does not exist
            os.makedirs(FOLDER_PATH, exist_ok=True)
            self.stdout.write(f"Using folder path: {FOLDER_PATH}")

            # Initialize RAGFlow
            self.stdout.write("Initializing RAGFlow connection...")
            try:
                rag_object = RAGFlow(api_key=API_KEY, base_url=RAGFLOW_URL)
            except Exception as e:
                raise CommandError(f"Failed to initialize RAGFlow: {e}")

            # Get Dataset
            dataset_rf = self._get_dataset(rag_object, DATASET_ID)

            document_ids = []

            if dataset_rf:
                process_items_in_parallel(
                    base_url=RI_BASE_URL,
                    base_url_rest=RI_BASE_URL_REST,
                    folder_path=FOLDER_PATH,
                    ragflow_dataset=dataset_rf,
                    document_ids=document_ids,
                    max_concurrent_tasks=MAX_CONCURRENT_TASKS,
                    limit_items=LIMIT_ITEMS,
                )
            else:
                raise CommandError(f"Dataset {DATASET_ID} is NONE")

            # Monitoring after dowloading
            tqdm.write("Starting document parsing monitoring...")
            asyncio.run(
                monitor_parsing(
                    dataset=dataset_rf,
                    document_ids=document_ids,
                    poll_interval=POLL_INTERVAL,
                )
            )

            # Final document status
            self._display_final_summary(dataset=dataset_rf)

        except Exception as e:
            raise CommandError(f"Error during ingest process: {e}")

    def _get_dataset(
        self, rag_object: RAGFlow, dataset_id: str
    ) -> Optional[DataSet]:
        """
        Get Ragflow dataset by dataset ID.
        """
        try:
            datasets = rag_object.list_datasets(id=dataset_id)
            if datasets:
                self.stdout.write(f"Using dataset ID: {dataset_id}")
                return datasets[0]
        except Exception as e:
            self.stderr.write(
                f"Cloud not use dataset ID: \
                {dataset_id}: {e}"
            )

    def _display_final_summary(self, dataset: DataSet) -> None:
        """
        Display final summary of processed documents.
        """
        try:
            documents = dataset.list_documents()
            self.stdout.write("\nFinal Summary: ")
            self.stdout.write("-" * 50)
            for doc in documents:
                self.stdout.write(
                    f"{doc.name} | Status: {doc.run} |\
                    Fragments: {doc.chunk_count}"
                )
            self.stdout.write("-" * 50)
            self.stdout.write("Process completed successfully")
        except Exception as e:
            self.stderr.write(f"Could not retrieve final document status: {e}")
