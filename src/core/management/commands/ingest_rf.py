"""
Django command to run the ingest pipeline from RI to Rag Flow.
"""

import asyncio
import os

from django.core.management.base import BaseCommand, CommandError
from ingest_ragflow.dspace_api.files import (
    get_files_from_metadata,
    get_item_details,
)
from ingest_ragflow.rag.dataset import get_dataset_by_id
from ingest_ragflow.rag.files import (
    get_docs_ids,
    get_orphaned_documents,
    remove_temp_pdf,
)
from ingest_ragflow.rag.parsing import (
    filter_done_documents,
    monitor_parsing,
    process_items_in_parallel,
)
from ingest_ragflow.rag.reporting import display_final_summary
from ragflow_sdk import RAGFlow
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
            "--folder_path",
            required=False,
            default="ingest_tmp",
            type=str,
            help="Folder path for downloaded files",
        )
        parser.add_argument(
            "--max_tasks",
            required=False,
            default=3,
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
            RAGFLOW_BASE_URL = os.getenv("RAGFLOW_BASE_URL")
            DATASET_ID = os.getenv("DATASET_ID")

            # Proxy set up
            http_proxy = os.getenv("HTTP_PROXY_RI")
            https_proxy = os.getenv("HTTPS_PROXY_RI")
            proxies = None
            if http_proxy or https_proxy:
                proxies = {"http": http_proxy, "https": https_proxy}
            self.stdout.write(
                f"Proxies: {proxies if proxies else 'No proxies configured'}"
            )

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
            if not RAGFLOW_BASE_URL:
                raise CommandError("RAGFLOW_BASE_URL not found in settings")
            if not DATASET_ID:
                raise CommandError("DATASET_ID not found in settings")

            # Remove '/api/v1'
            if RAGFLOW_BASE_URL and RAGFLOW_BASE_URL.endswith("/api/v1"):
                RAGFLOW_BASE_URL = RAGFLOW_BASE_URL[:-7]
                self.stdout.write(f"RAGFlow URL: {RAGFLOW_BASE_URL}")

            # Create output directory if it does not exist
            os.makedirs(FOLDER_PATH, exist_ok=True)
            self.stdout.write(f"Using folder path: {FOLDER_PATH}")

            # Initialize RAGFlow
            self.stdout.write("Initializing RAGFlow connection...")
            try:
                rag_object = RAGFlow(
                    api_key=API_KEY, base_url=RAGFLOW_BASE_URL
                )
            except Exception as e:
                raise CommandError(f"Failed to initialize RAGFlow: {e}")

            # Get Dataset
            dataset_rf = get_dataset_by_id(rag_object, DATASET_ID)

            # Get existing repository UUIDs from database
            existing_repository_uuids = self._get_existing_repository_uuids()
            self.stdout.write(
                f"Found {len(existing_repository_uuids)} existing documents"
                " in database"
            )

            document_ids = []
            metadata_map = {}

            self.stdout.write(f"Limit items: {LIMIT_ITEMS}")

            if dataset_rf:
                # Remove failed/canceled documents
                failed_documents_ids = get_docs_ids(
                    dataset=dataset_rf, statuses=["FAIL", "CANCEL"]
                )

                if len(failed_documents_ids) > 0:
                    self.stdout.write(
                        f"Found {len(failed_documents_ids)} "
                        "documents with FAIL/CANCEL status."
                    )
                    dataset_rf.delete_documents(ids=failed_documents_ids)

                # recover orphaned documents mechanism
                orphaned_documents = get_orphaned_documents(
                    dataset=dataset_rf,
                    existing_uuids=existing_repository_uuids,
                    status="DONE",
                )

                self.stdout.write(
                    f"There are {len(orphaned_documents)} "
                    "orphaned documents.\n"
                )

                if orphaned_documents:
                    self.stdout.write(
                        "Registering orphaned documents in database..."
                    )
                    orphaned_metadata_map = {}
                    for (
                        ragflow_id,
                        uuid,
                    ) in orphaned_documents.items():
                        metadata = get_item_details(
                            base_url_rest=RI_BASE_URL_REST,
                            item_id=uuid,
                            proxies=proxies,
                        )
                        orphaned_metadata_map[ragflow_id] = metadata
                    self._create_documents(orphaned_metadata_map)
                    self.stdout.write(
                        f"Successfully registered {len(orphaned_documents)} "
                        "orphaned documents"
                    )
                    display_final_summary(
                        dataset=dataset_rf, metadata_map=orphaned_metadata_map
                    )
                    existing_repository_uuids = (
                        self._get_existing_repository_uuids()
                    )
                    self.stdout.write(
                        f"Found {len(existing_repository_uuids)} "
                        "existing documents in database"
                    )

                metadata_map = process_items_in_parallel(
                    base_url=RI_BASE_URL,
                    base_url_rest=RI_BASE_URL_REST,
                    folder_path=FOLDER_PATH,
                    ragflow_dataset=dataset_rf,
                    document_ids=document_ids,
                    max_concurrent_tasks=MAX_CONCURRENT_TASKS,
                    limit_items=LIMIT_ITEMS,
                    exclude_uuids=existing_repository_uuids,
                    proxies=proxies,
                )
            else:
                raise CommandError(f"Dataset {DATASET_ID} is NONE")

            if not document_ids:
                self.stdout.write(
                    "No new documents to ingest. All items are already"
                    " in the database."
                )
                return

            # Monitoring after dowloading
            tqdm.write("Starting document parsing monitoring...")
            asyncio.run(
                monitor_parsing(
                    dataset=dataset_rf,
                    document_ids=document_ids,
                    poll_interval=POLL_INTERVAL,
                )
            )

            # Filter metadata_map to only include documents with DONE status
            metadata_map_done = filter_done_documents(dataset_rf, metadata_map)
            self.stdout.write(
                f"Documents with DONE status: {len(metadata_map_done)} out\
                 of {len(metadata_map)}"
            )

            # populate metadata in Document table
            self._create_documents(metadata_map_done)

            # get list of processed files (status DONE)
            processed_file_names = get_files_from_metadata(metadata_map_done)

            # remove files
            remove_temp_pdf(
                folder_path=FOLDER_PATH,
                processed_file_names=processed_file_names,
            )

            # Final document status
            display_final_summary(
                dataset=dataset_rf, metadata_map=metadata_map
            )

        except Exception as e:
            raise CommandError(f"Error during ingest process: {e}")

    def _get_existing_repository_uuids(self) -> set[str]:
        """
        Get all existing repository IDs (UUIDs) from the Document table.
        """
        try:
            from core.models import Document

            existing_uuids = set(
                Document.objects.values_list("repository_id", flat=True)
            )
            return existing_uuids
        except ImportError:
            self.stderr.write(
                "Error: Could not import Document model from core.models"
            )
            return set()
        except Exception as e:
            self.stderr.write(f"Error retrieving existing repository IDs: {e}")
            return set()

    def _determine_document_status(self, item_metadata: dict) -> str:
        """
        Determine document status based on metadata.
        """
        metadata = item_metadata.get("metadata", {})

        dc_rights = metadata.get("dc.rights", "").lower()

        if dc_rights:
            if (
                "abierto" in dc_rights
                or "open" in dc_rights
                or "libre" in dc_rights
            ):
                return "L"
            elif "restringido" in dc_rights or "restricted" in dc_rights:
                return "R"
            elif "embargo" in dc_rights or "embargoed" in dc_rights:
                return "E"

        in_archive = item_metadata.get("inArchive", False)
        discoverable = item_metadata.get("discoverable", False)
        withdrawn = item_metadata.get("withdrawn", False)

        if withdrawn:
            return "R"

        if in_archive and discoverable:
            return "L"

        return "R"

    def _create_documents(self, metadata_map: dict) -> None:
        """
        Create Document records in database.
        """
        try:
            from core.models import Document

            created_count = 0
            update_count = 0
            error_count = 0

            RI_BASE_URL = os.getenv("RI_BASE_URL")

            for ragflow_id, item_metadata in metadata_map.items():
                try:
                    title = item_metadata.get("name", "Unknown Title")
                    repository_id = item_metadata.get("uuid", "")
                    handle = item_metadata.get("handle", "")

                    if handle:
                        repository_uri = (
                            f"{RI_BASE_URL}/xmlui/handle/{handle}"
                            if handle
                            else ""
                        )
                    else:
                        repository_uri = ""

                    status = self._determine_document_status(
                        item_metadata=item_metadata
                    )

                    _, created = Document.objects.update_or_create(
                        repository_id=repository_id,
                        defaults={
                            "id": ragflow_id,
                            "title": title,
                            "repository_uri": repository_uri,
                            "status": status,
                        },
                    )

                    if created:
                        created_count += 1
                        self.stdout.write(f"Created document: {title}")
                    else:
                        update_count += 1
                        self.stdout.write(f"Updated document: {title}")
                except Exception as e:
                    error_count += 1
                    self.stderr.write(
                        f"Error processing document rf_id: {ragflow_id}: {e}"
                    )

            self.stdout.write(
                f"Successfully processed {len(metadata_map)} documents: "
                f"{created_count} created, {update_count} updated,"
                f"{error_count} errors"
            )
        except ImportError:
            self.stderr.write(
                "Error: Could not import Document model from core.models"
            )
        except Exception as e:
            self.stderr.write(f"Error creating Django documents: {e}")
            raise
