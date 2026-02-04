from functools import lru_cache
from pydantic_settings import BaseSettings
from enum import StrEnum


class VectorDBProvider(StrEnum):
    QDRANT = "qdrant"
    REDIS = "redis"

class VectorDBSettings(BaseSettings):
    VECTOR_DB_PROVIDER: VectorDBProvider

@lru_cache
def get_vector_db_settings() -> VectorDBSettings:
    return VectorDBSettings()
