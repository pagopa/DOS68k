from typing import Annotated
from pydantic import Field
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    frontend_url: Annotated[str, Field(default="http://localhost")]

settings: Settings = Settings()