from functools import lru_cache
from pydantic_settings import BaseSettings


class LangfuseSettings(BaseSettings):
    LANGFUSE_PUBLIC_KEY: str = ""
    LANGFUSE_SECRET_KEY: str = ""
    LANGFUSE_HOST: str = "https://cloud.langfuse.com"
    LANGFUSE_FLUSH_AT: int = 15
    LANGFUSE_FLUSH_INTERVAL_S: float = 0.5


@lru_cache()
def get_langfuse_settings() -> LangfuseSettings:
    return LangfuseSettings()
