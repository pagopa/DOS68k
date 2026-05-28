from functools import lru_cache
from typing import Annotated
from pydantic import Field, PositiveInt
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    FRONTEND_URL: Annotated[str, Field(default="http://localhost")]
    LOG_LEVEL: Annotated[
        PositiveInt, Field(default=20, description="Default 20 for INFO")
    ]
    QUERY_TABLENAME: Annotated[str, Field(default="queries")]
    SESSIONS_TABLENAME: Annotated[str, Field(default="sessions")]
    EVALUATE_UPPER_LIMIT: Annotated[int, Field(default=50)]


@lru_cache()
def get_settings() -> Settings:
    return Settings()
