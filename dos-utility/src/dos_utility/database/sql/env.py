from functools import lru_cache
from typing import Annotated
from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings

class DBSettings(BaseSettings):
    DB_USERNAME: Annotated[str, Field(default="postgres")]
    DB_PASSWORD: Annotated[SecretStr, Field(default="password")]
    DB_HOST: Annotated[str, Field(default="localhost")]
    DB_PORT: Annotated[int, Field(default=5432)]
    DB_NAME: Annotated[str, Field(default="db")]

@lru_cache()
def get_db_settings() -> DBSettings:
    return DBSettings()
