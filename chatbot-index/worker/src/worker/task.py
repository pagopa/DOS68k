import json
from logging import Logger
from typing import Any
from llama_index.core.vector_stores import MetadataFilter, MetadataFilters
from llama_index.core.vector_stores.types import FilterOperator

from loaders import get_document_loader, Message, Document
from parsers import get_parser, ChunkData
from embedder import get_embedder
from env import get_task_settings, get_global_settings, GlobalSettings

from dos_utility.vector_db import get_vector_db_ctx, ObjectData
from dos_utility.utils.logger import get_logger



async def process_task(body: bytes) -> None:
    """Process a task with the given body.

    Args:
        body (bytes): The body of the task to be processed.
    """
    settings: GlobalSettings = get_global_settings()
    logger: Logger = get_logger(name=__file__, level=settings.log_level)
    task_settings = get_task_settings()

    loader = get_document_loader(bucket_name=task_settings.bucket_name)
    parser = get_parser(
        chunk_size = task_settings.embed_chunk_size,
        chunk_overlap = task_settings.embed_chunk_overlap
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
    converted_data: Any = json.loads(body.decode("utf-8"))
    
    message = Message(**converted_data)
    document: Document = loader.read(message=message)

    logger.info(f"Document {message.objectKey} retrieved from bucket. Start indexing...")
    chunks: ChunkData = parser.transform(document=document)
    data_to_store: ObjectData = embedder.transform(chunks=chunks)

    async with get_vector_db_ctx() as vector_db:
        indexes = await vector_db.get_indexes()
        doc_to_delete = []
        if message.indexId not in indexes:
            await vector_db.create_index(
                index_name=message.indexId, vector_dim=task_settings.embed_dim
            )
        else:
            filters = MetadataFilters(
                filters=[
                    MetadataFilter(
                        key= "filename",
                        value= message.objectKey,
                        operator = FilterOperator.TEXT_MATCH
                    )
                ]
            )
            results = await vector_db.filter_search(
                index_name = message.indexId,
                max_results = 10000,
                filters = filters
            )

            doc_to_delete.extend([x.id for x in results])
        
        try:
            logger.info(f"Adding {len(data_to_store)} chunks to index '{message.indexId}' ")
            await vector_db.put_objects(data=data_to_store, index_name=message.indexId)
        finally:
            logger.info(f"{len(data_to_store)} chunks removed from index '{message.indexId}'")
            await vector_db.delete_objects(index_name = message.indexId, ids = doc_to_delete)
        
        logger.info(f"{len(data_to_store)} chunks from document '{message.objectKey}' added to index '{message.indexId}'")

