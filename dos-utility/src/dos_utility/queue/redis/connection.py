from functools import lru_cache
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from redis.asyncio import Redis, ConnectionPool

from .env import queue_settings

@lru_cache
def get_queue_pool() -> ConnectionPool:
    return ConnectionPool.from_url(url=f"redis://{queue_settings.QUEUE_HOST}:{queue_settings.QUEUE_PORT}/0", decode_responses=True)

async def get_queue_client() -> AsyncGenerator[Redis, None]:
    redis_client: Redis = Redis(connection_pool=get_queue_pool())

    try:
        yield redis_client
    finally:
        await redis_client.aclose()

@asynccontextmanager
async def get_queue_client_ctx() -> AsyncGenerator[Redis, None]:
    async_generator: AsyncGenerator[Redis, None] = get_queue_client()
    client: Redis = await async_generator.__anext__()

    try:
        yield client
    finally:
        await async_generator.aclose()
