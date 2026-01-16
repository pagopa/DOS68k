from typing import Annotated
from pydantic import Field
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    frontend_url: Annotated[str, Field(default="http://localhost")]

class QueueSettings(BaseSettings):
    QUEUE_HOST: Annotated[str, Field(default="localhost")]
    QUEUE_PORT: Annotated[int, Field(default=6379)]

settings: Settings = Settings()
queue_settings: QueueSettings = QueueSettings()