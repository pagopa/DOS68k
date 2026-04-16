from functools import lru_cache
from pathlib import Path
from typing import Annotated, Optional, Literal
from pydantic import Field, PositiveInt, PositiveFloat, NonNegativeFloat
from pydantic_settings import BaseSettings


class EmbeddingsSettings(BaseSettings):
    # LLM / Embedding provider ("google", "mock")
    provider: Annotated[Literal["google", "mock"], Field(default="mock")]
    model_api_key: Annotated[
        Optional[str],
        Field(
            default=None,
            description="API key for the chosen provider. Do not set if provider is 'mock'",
        ),
    ]

    # Embedding settings
    embed_model_id: Annotated[str, Field(default="mock")]
    embed_batch_size: Annotated[PositiveInt, Field(default=100)]
    embed_dim: Annotated[PositiveInt, Field(default=768)]
    embed_task: Annotated[str, Field(default="RETRIEVAL_DOCUMENT")]
    embed_retries: Annotated[PositiveInt, Field(default=3)]
    embed_retry_min_seconds: Annotated[PositiveFloat, Field(default=1.0)]

    # Retrieval settings
    similarity_topk: Annotated[PositiveInt, Field(default=5)]
    use_async: Annotated[bool, Field(default=True)]


@lru_cache
def get_embedding_settings() -> EmbeddingsSettings:
    return EmbeddingsSettings()


settings: EmbeddingsSettings = EmbeddingsSettings()
