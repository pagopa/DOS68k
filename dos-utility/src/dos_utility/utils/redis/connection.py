from functools import lru_cache
from redis.asyncio import ConnectionPool
from typing import Optional

from .env import RedisConnectionSettings, get_redis_connection_settings

@lru_cache
def get_redis_connection_pool(decode_responses: Optional[bool]=None) -> ConnectionPool:
    """Get a Redis connection pool.

    Args:
        decode_responses (Optional[bool]): Whether to decode responses to str. Defaults to None.
    """
    connection_settings: RedisConnectionSettings = get_redis_connection_settings()

    if decode_responses is not None:
        return ConnectionPool.from_url(
            url=f"redis://{connection_settings.REDIS_HOST}:{connection_settings.REDIS_PORT}/0",
            decode_responses=decode_responses,
        )

    return ConnectionPool.from_url(url=f"redis://{connection_settings.REDIS_HOST}:{connection_settings.REDIS_PORT}/0")
