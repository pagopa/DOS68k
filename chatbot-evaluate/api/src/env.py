from functools import lru_cache
from typing import Annotated
from pydantic import Field
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    frontend_url: Annotated[str, Field(default="http://localhost")]

@lru_cache()
def get_settings() -> Settings:
    return Settings()
