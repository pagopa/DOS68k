from typing import AsyncGenerator
from redis.asyncio import Redis, ConnectionPool

from .env import queue_settings

def __get_queue_pool() -> ConnectionPool:
    return ConnectionPool.from_url(url=f"redis://{queue_settings.QUEUE_HOST}:{queue_settings.QUEUE_PORT}/0", decode_responses=True)

async def get_queue_client() -> AsyncGenerator[Redis, None]:
    redis_client: Redis = Redis(connection_pool=__get_queue_pool())

    try:
        yield redis_client
    finally:
        pass