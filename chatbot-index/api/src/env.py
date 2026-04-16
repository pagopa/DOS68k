from functools import lru_cache
from typing import Annotated
from pydantic import Field, PositiveInt
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    frontend_url: Annotated[str, Field(default="http://localhost")]
    log_level: Annotated[PositiveInt, Field(default=20)]

class IndexBucketSettings(BaseSettings):
    index_documents_bucket_name: str


@lru_cache()
def get_settings() -> Settings:
    return Settings()

@lru_cache
def get_index_bucket_settings() -> IndexBucketSettings:
    return IndexBucketSettings()