from functools import lru_cache
from typing import Annotated
from pydantic import Field, PositiveInt
from pydantic_settings import BaseSettings


class EmbeddingsSettings(BaseSettings):
    embed_dim: Annotated[PositiveInt, Field(default=768)]


@lru_cache
def get_embedding_settings() -> EmbeddingsSettings:
    return EmbeddingsSettings()
