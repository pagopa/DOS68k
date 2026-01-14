from redis.asyncio import Redis, ConnectionPool
from typing import AsyncGenerator
from functools import lru_cache

from .env import queue_settings

@lru_cache()
def __get_queue_pool() -> ConnectionPool:
    return ConnectionPool.from_url(url=f"redis://{queue_settings.QUEUE_HOST}:{queue_settings.QUEUE_PORT}/0", decode_responses=True)

async def get_queue_client() -> AsyncGenerator[Redis, None]:
    client: Redis = Redis(connection_pool=__get_queue_pool())

    try:
        yield client
    finally:
        # We do not need to close the client as it uses a connection pool which manages connections itself
        pass
