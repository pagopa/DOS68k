import json
from typing import Any

from loaders import get_document_loader, Message, Document
from parsers import get_parser, ChunkData
from embedder import get_embedder, ObjectData
from env import get_task_settings

from dos_utility.vector_db import get_vector_db_ctx

task_settings = get_task_settings()
loader = get_document_loader(bucket_name=task_settings.bucket_name)
parser = get_parser()
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


async def process_task(body: bytes) -> None:
    """Process a task with the given body.

    Args:
        body (bytes): The body of the task to be processed.
    """
    converted_data: Any = json.loads(body.decode("utf-8"))

    message = Message(**converted_data)

    document: Document = loader.read(message=message)
    chunks: ChunkData = parser.transform(document=document)
    data_to_store: ObjectData = embedder.transform(chunks=chunks)

    async with get_vector_db_ctx() as vector_db:
        indexes = await vector_db.get_indexes()
        if message.indexId not in indexes:
            await vector_db.create_index(
                index_name=message.indexId, vector_dim=task_settings.embed_dim
            )
        await vector_db.put_objects(data=data_to_store, index_name=message.indexId)
