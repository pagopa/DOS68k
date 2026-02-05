from functools import lru_cache
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Annotated


class QdrantVectorDBSettings(BaseSettings):
    QDRANT_HOST: Annotated[str, Field(default="localhost")]
    QDRANT_PORT: Annotated[int, Field(default=6333)]

@lru_cache()
def get_qdrant_vector_db_settings() -> QdrantVectorDBSettings:
    return QdrantVectorDBSettings()