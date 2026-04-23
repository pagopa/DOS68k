from functools import lru_cache
from pydantic_settings import BaseSettings
from typing import Annotated, Literal
from pydantic import Field, PositiveInt, PositiveFloat


class TaskSettings(BaseSettings):
    provider: Literal["google"]

    # Bucket
    storage_provider: str
    bucket_name: str

    # Vector DB
    vector_db_provider: str

    # Embedding settings
    embed_chunk_size: Annotated[
        int, Field(default="Chunk size in number of tokens")
    ]
    embed_chunk_overlap: Annotated[
        int, Field(default="Number of overlapping tokens between consecutive chunks")
    ]

    embed_model_id: Annotated[
        str, Field(default="ID of the embedding model for the chose provider")
    ]
    embed_batch_size: Annotated[PositiveInt, Field(default=100)]
    embed_dim: Annotated[PositiveInt, Field(default=768)]
    embed_task: Annotated[str, Field(default="RETRIEVAL_DOCUMENT")]
    embed_retries: Annotated[PositiveInt, Field(default=3)]
    embed_retry_min_seconds: Annotated[PositiveFloat, Field(default=1.0)]
    model_api_key: Annotated[str, Field(description="API key for the chosen provider")]

class GlobalSettings(BaseSettings):
    log_level: Annotated[PositiveInt, Field(default=20)]


@lru_cache
def get_task_settings() -> TaskSettings:
    return TaskSettings()

@lru_cache
def get_global_settings() -> GlobalSettings:
    return GlobalSettings()