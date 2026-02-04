from functools import lru_cache
from typing import Annotated
from pydantic import Field
from pydantic_settings import BaseSettings

class RedisConnectionSettings(BaseSettings):
    REDIS_HOST: Annotated[str, Field(default="localhost")]
    REDIS_PORT: Annotated[int, Field(default=6379)]

@lru_cache()
def get_redis_connection_settings() -> RedisConnectionSettings:
    return RedisConnectionSettings()
