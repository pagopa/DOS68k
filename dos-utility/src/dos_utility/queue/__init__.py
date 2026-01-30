from contextlib import asynccontextmanager
from typing import AsyncGenerator
from .env import QueueProvider, QueueSettings, get_queue_settings

from .interface import QueueInterface
from .redis import get_redis_queue
from .sqs import get_sqs_queue


__all__ = [
    "get_queue_client",
    "get_queue_client_ctx",
    "QueueInterface",
]


@asynccontextmanager
async def get_queue_client_ctx() -> AsyncGenerator[QueueInterface, None]:
    """Asynchronous context manager to get the appropriate queue client based on configuration.

    Yields:
        AsyncGenerator[QueueInterface, None]: An instance of the appropriate queue client.

    Examples:
        >>> async with get_queue_client_ctx() as queue_client:
        >>>     msg_id = await queue_client.enqueue(msg=b"Hello World!")
    """
    queue_settings: QueueSettings = get_queue_settings() # Get env variable values

    if queue_settings.QUEUE_PROVIDER is QueueProvider.REDIS:
        queue: QueueInterface = get_redis_queue()
    elif queue_settings.QUEUE_PROVIDER is QueueProvider.SQS:
        queue: QueueInterface = get_sqs_queue()

    async with queue as queue_client:
        yield queue_client

# FastAPI dependency
async def get_queue_client() -> AsyncGenerator[QueueInterface, None]:
    """FastAPI dependency to get the appropriate queue client based on configuration.

    Yields:
        AsyncGenerator[QueueInterface, None]: An instance of the appropriate queue client.

    Examples:
        >>> @app.post("/enqueue")
        >>> async def enqueue_message(queue_client: Annotated[QueueInterface, Depends(get_queue_client)]):
        >>>     msg_id = await queue_client.enqueue(msg=b"Hello World!")
    """
    async with get_queue_client_ctx() as queue_client:
        yield queue_client
