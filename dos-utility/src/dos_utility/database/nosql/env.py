from functools import lru_cache
from pydantic_settings import BaseSettings
from enum import StrEnum

class NoSQLProvider(StrEnum):
    DYNAMODB = "dynamodb"

class NoSQLSettings(BaseSettings):
    NOSQL_PROVIDER: NoSQLProvider

@lru_cache()
def get_nosql_settings() -> NoSQLSettings:
    return NoSQLSettings()