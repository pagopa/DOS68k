from enum import StrEnum
from functools import lru_cache
from typing import Annotated
from pydantic import Field
from pydantic_settings import BaseSettings


class TracingProvider(StrEnum):
    NOOP = "noop"
    LANGFUSE = "langfuse"


class TracingSettings(BaseSettings):
    TRACING_PROVIDER: Annotated[TracingProvider, Field(default=TracingProvider.NOOP)]


@lru_cache()
def get_tracing_settings() -> TracingSettings:
    return TracingSettings()
