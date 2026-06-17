import json
from logging import Logger
from typing import Any
from llama_index.core.vector_stores import MetadataFilter, MetadataFilters
from llama_index.core.vector_stores.types import FilterOperator

from loaders import get_document_loader, Message, Document
from parsers import get_parser, ChunkData
from embedder import get_embedder
from env import (
    get_task_settings,
    TaskSettings,
    get_global_settings,
    GlobalSettings,
    get_storage_settings,
    StorageSettings,
)

from dos_utility.vector_db import get_vector_db_ctx, ObjectData
from dos_utility.utils.logger import get_logger


async def process_task(body: bytes) -> None:
    """Process a task with the given body.

    Args:
        body (bytes): The body of the task to be processed.
    """
    settings: GlobalSettings = get_global_settings()
    task_settings: TaskSettings = get_task_settings()
    storage_settings: StorageSettings = get_storage_settings()
    logger: Logger = get_logger(name=__name__, level=settings.log_level)

    logger.debug("Initializing document loader, parser, and embedder...")

    loader = get_document_loader(
        bucket_name=storage_settings.index_documents_bucket_name
    )
    parser = get_parser(
        chunk_size=task_settings.embed_chunk_size,
        chunk_overlap=task_settings.embed_chunk_overlap,
    )
    embedder = get_embedder(
        provider=task_settings.provider,
        embed_model_id=task_settings.embed_model_id,
        embed_batch_size=task_settings.embed_batch_size,
        embed_dim=task_settings.embed_dim,
        embed_task=task_settings.embed_task,
        embed_retries=task_settings.embed_retries,
        embed_retry_min_seconds=task_settings.embed_retry_min_seconds,
        model_api_key=task_settings.model_api_key,
    )

    logger.debug("Parsing task body...")
    converted_data: Any = json.loads(body.decode("utf-8"))
    message = Message(**converted_data)

    logger.info(
        f"Processing document '{message.object_key}' (index: '{message.index_id}')"
    )

    document: Document = loader.read(message=message)
    logger.debug(
        f"Document '{message.object_key}' retrieved from bucket. Starting chunking..."
    )

    chunks: ChunkData = parser.transform(document=document)
    logger.debug(
        f"Document '{message.object_key}' chunked into {len(chunks)} chunks. Starting embedding..."
    )

    data_to_store: ObjectData = embedder.transform(chunks=chunks)
    logger.info(
        f"Successfully embedded {len(data_to_store)} chunks. Preparing to store in vector DB..."
    )

    async with get_vector_db_ctx() as vector_db:
        indexes = await vector_db.get_indexes()

        doc_to_delete = []

        if message.index_id not in indexes:
            logger.info(f"Index '{message.index_id}' not found. Creating new index")
            await vector_db.create_index(
                index_name=message.index_id, vector_dim=task_settings.embed_dim
            )
            logger.debug(f"Index '{message.index_id}' created successfully")
        else:
            logger.debug(
                f"Index '{message.index_id}' already exists. Searching for existing chunks to delete..."
            )
            filters = MetadataFilters(
                filters=[
                    MetadataFilter(
                        key="filename",
                        value=message.object_key,
                        operator=FilterOperator.TEXT_MATCH,
                    )
                ]
            )
            results = await vector_db.filter_search(
                index_name=message.index_id, max_results=10000, filters=filters
            )

            doc_to_delete.extend([x.id for x in results])
            logger.debug(f"Found {len(doc_to_delete)} existing chunks to delete")

        try:
            logger.info(f"Adding {len(data_to_store)} new chunks...")
            await vector_db.put_objects(data=data_to_store, index_name=message.index_id)
            logger.debug(f"Successfully added {len(data_to_store)} chunks")
        finally:
            if doc_to_delete:
                logger.debug(f"Deleting {len(doc_to_delete)} old chunks...")
                await vector_db.delete_objects(
                    index_name=message.index_id, ids=doc_to_delete
                )
                logger.info(f"Old chunks deleted")
            else:
                logger.debug("No old chunks to delete")
