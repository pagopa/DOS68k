from functools import lru_cache
from typing import Annotated
from pydantic import Field
from pydantic_settings import BaseSettings


class LangfuseSettings(BaseSettings):
    LANGFUSE_PUBLIC_KEY: Annotated[str, Field(default="")]
    LANGFUSE_SECRET_KEY: Annotated[str, Field(default="")]
    LANGFUSE_HOST: Annotated[str, Field(default="https://cloud.langfuse.com")]
    LANGFUSE_FLUSH_AT: Annotated[int, Field(default=15)]
    LANGFUSE_FLUSH_INTERVAL_S: Annotated[float, Field(default=0.5)]


@lru_cache()
def get_langfuse_settings() -> LangfuseSettings:
    return LangfuseSettings()
