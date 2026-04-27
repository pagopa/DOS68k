from functools import lru_cache
from typing import Annotated
from pydantic import Field, PositiveInt
from pydantic_settings import BaseSettings


class SessionSettings(BaseSettings):
    SESSIONS_TABLENAME: Annotated[str, Field(default="sessions")]
    SESSION_EXPIRATION_DAYS: PositiveInt


@lru_cache
def get_session_settings() -> SessionSettings:
    return SessionSettings()
