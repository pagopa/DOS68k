from functools import lru_cache
from typing import Annotated
from pydantic import Field
from pydantic_settings import BaseSettings


class QuerySettings(BaseSettings):
    QUERY_TABLENAME: Annotated[str, Field(default="queries")]

@lru_cache
def get_query_settings() -> QuerySettings:
    return QuerySettings()