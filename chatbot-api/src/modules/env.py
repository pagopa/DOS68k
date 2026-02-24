from functools import lru_cache
from pydantic import PositiveInt
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    session_expiration_days: PositiveInt

@lru_cache
def get_settings() -> Settings:
    return Settings()