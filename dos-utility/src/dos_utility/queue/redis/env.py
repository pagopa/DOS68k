from functools import lru_cache
from typing import Annotated
from pydantic import Field
from pydantic_settings import BaseSettings

class RedisQueueSettings(BaseSettings):
    REDIS_STREAM: Annotated[str, Field(default="my-stream")]
    REDIS_GROUP: Annotated[str, Field(default="my-group")]

@lru_cache()
def get_redis_queue_settings() -> RedisQueueSettings:
    return RedisQueueSettings()