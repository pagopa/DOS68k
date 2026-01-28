from functools import lru_cache
from redis.asyncio import ConnectionPool

from .env import RedisQueueSettings, get_redis_queue_settings

@lru_cache
def get_queue_pool() -> ConnectionPool:
    queue_settings: RedisQueueSettings = get_redis_queue_settings()

    return ConnectionPool.from_url(
        url=f"redis://{queue_settings.REDIS_HOST}:{queue_settings.REDIS_PORT}/0",
        decode_responses=False, # Do NOT decode responses to str (keep as bytes for message body)
    )
