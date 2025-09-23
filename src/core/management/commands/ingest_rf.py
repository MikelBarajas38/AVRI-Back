"""
Django command to run the ingest pipeline from RI to Rag Flow.
"""

import asyncio
import os

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from ingest_ragflow.rag.parsing import (
    monitor_parsing,
    process_items_in_parallel,
)
from ragflow_sdk import RAGFlow


class Command(BaseCommand):
    help = "Run the ingest pipeline from RI to RAG Flow"

    def add_arguments(self, parser):
        parser.add_argument(
            "--li",
            type=int,
            default=None,
            help="Total number of retrieve items (optional)",
        )
        parser.add_argument(
            "--folder_path",
            type=str,
            help="Folder path for downloaded files (optional, defaults to\
                                                    media/ingest_temp)",
        )
        parser.add_argument(
            "--max_tasks",
            type=int,
            default=8,
            help="Maximum number of concurrent tasks",
        )
        parser.add_argument(
            "--poll_interval",
            type=float,
            default=2.5,
            help="Interval (in seconds) between status checks",
        )
        parser.add_argument(
            "--dataset_id",
            type=str,
            help="Specific dataset ID to use (optional, will prompt \
                if not provided)",
        )

    def handle(self, *args, **options):
        try:
            # Configuration from environment variables
            api_key = os.getenv("RAGFLOW_API_KEY")
            ragflow_url = os.getenv("RAGFLOW_BASE_URL")
            default_dataset_id = os.getenv("DATASET_ID")

            # Fix URL if it already contains /api/v1
            # (SDK adds it automatically)
            if ragflow_url and ragflow_url.endswith("/api/v1"):
                ragflow_url = ragflow_url[:-7]  # Remove '/api/v1' from the end
                self.stdout.write(
                    f"Adjusted RAGFlow URL (removed /api/v1): {ragflow_url}"
                )

            # Validate required environment variables
            if not api_key:
                raise CommandError("RAGFLOW_API_KEY not found in settings")
            if not ragflow_url:
                raise CommandError("RAGFLOW_BASE_URL not found in settings")

            # Set up parameters
            BASE_URL = "https://repositorioinstitucional.uaslp.mx/"
            BASE_URL_REST = "https://repositorioinstitucional.uaslp.mx/rest"
            LIMIT_ITEMS = options["li"]
            MAX_CONCURRENT_TASKS = options["max_tasks"]
            POLL_INTERVAL = options["poll_interval"]

            # Set folder path
            if options["folder_path"]:
                FOLDER_PATH = options["folder_path"]
            else:
                # Default to media/ingest_temp
                FOLDER_PATH = os.path.join(settings.MEDIA_ROOT, "ingest_temp")

            # Create output directory if it does not exist
            os.makedirs(FOLDER_PATH, exist_ok=True)
            self.stdout.write(f"Using folder path: {FOLDER_PATH}")

            # Initialize RAGFlow
            self.stdout.write("Initializing RAGFlow connection...")
            try:
                rag_object = RAGFlow(api_key=api_key, base_url=ragflow_url)
            except Exception as e:
                raise CommandError(f"Failed to initialize RAGFlow: {e}")

            # Get or select dataset
            dataset = self._get_dataset(
                rag_object, options["dataset_id"], default_dataset_id
            )

            self.stdout.write(f"Using dataset: {dataset.name}")
            self.stdout.write("Starting document retrieval and processing...")

            # List of documents for monitoring
            document_ids = []

            # Run the main processing pipeline
            process_items_in_parallel(
                base_url=BASE_URL,
                base_url_rest=BASE_URL_REST,
                folder_path=FOLDER_PATH,
                ragflow_dataset=dataset,
                document_ids=document_ids,
                max_concurrent_tasks=MAX_CONCURRENT_TASKS,
                limit_items=LIMIT_ITEMS,
            )

            # Monitor parsing after downloading
            self.stdout.write("Starting document parsing monitoring...")
            asyncio.run(monitor_parsing(dataset, document_ids, POLL_INTERVAL))

            # Final document status
            self._display_final_summary(dataset)

            self.stdout.write(
                self.style.SUCCESS(
                    "Process \
            completed successfully."
                )
            )

        except Exception as e:
            raise CommandError(f"Error during ingest process: {e}")

    def _get_dataset(self, rag_object, dataset_id_option, default_dataset_id):
        """
        Get dataset either from parameter, environment
        variable, or user selection.
        """

        # If dataset_id provided as option, use it
        if dataset_id_option:
            try:
                datasets = rag_object.list_datasets(id=dataset_id_option)
                if datasets:
                    return datasets[0]
                else:
                    raise CommandError(
                        f"Dataset with ID \
                    {dataset_id_option} not found"
                    )
            except Exception as e:
                raise CommandError(
                    f"Error retrieving dataset \
                {dataset_id_option}: {e}"
                )

        # If default dataset ID in environment, use it
        if default_dataset_id:
            try:
                datasets = rag_object.list_datasets(id=default_dataset_id)
                if datasets:
                    self.stdout.write(
                        f"Using default dataset ID from \
                        environment: {default_dataset_id}"
                    )
                    return datasets[0]
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(
                        f"Could not use default dataset \
                        ID {default_dataset_id}: {e}"
                    )
                )

        # Interactive selection
        try:
            datasets = rag_object.list_datasets()
            if not datasets:
                raise CommandError("No datasets found in RAGFlow")

            self.stdout.write("Available datasets:")
            for i, dataset in enumerate(datasets):
                self.stdout.write(f"{i}: {dataset.name} (ID: {dataset.id})")

            while True:
                try:
                    selected_index = input("Enter dataset index: ")
                    selected_index = int(selected_index)
                    if 0 <= selected_index < len(datasets):
                        return rag_object.list_datasets(
                            id=datasets[selected_index].id
                        )[0]
                    else:
                        self.stdout.write(
                            "Invalid index. \
                        Please try again."
                        )
                except ValueError:
                    self.stdout.write(
                        "Please \
                        enter a valid number."
                    )
                except KeyboardInterrupt:
                    raise CommandError(
                        "Operation \
                    cancelled by user"
                    )

        except Exception as e:
            raise CommandError(f"Error listing datasets: {e}")

    def _display_final_summary(self, dataset):
        """
        Display final summary of processed documents.
        """
        try:
            documents = dataset.list_documents()
            self.stdout.write("\nFinal Summary:")
            self.stdout.write("-" * 50)
            for doc in documents:
                self.stdout.write(
                    f"{doc.name} | Status: {doc.run} |"
                    f"Fragments: {doc.chunk_count}"
                )
            self.stdout.write("-" * 50)
        except Exception as e:
            self.stdout.write(
                self.style.WARNING(
                    f"Could not retrieve final document status: {e}"
                )
            )
