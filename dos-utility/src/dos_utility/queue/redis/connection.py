from functools import lru_cache
from typing import Generator
from redis.asyncio import Redis, ConnectionPool

from .env import queue_settings

@lru_cache
def get_queue_pool() -> ConnectionPool:
    return ConnectionPool.from_url(url=f"redis://{queue_settings.QUEUE_HOST}:{queue_settings.QUEUE_PORT}/0", decode_responses=True)

def get_queue_client() -> Generator[Redis, None, None]:
    redis_client: Redis = Redis(connection_pool=get_queue_pool())

    try:
        yield redis_client
    finally:
        pass
