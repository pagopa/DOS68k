from typing import Annotated
from pydantic import Field
from pydantic_settings import BaseSettings

class QueueSettings(BaseSettings):
    QUEUE_HOST: Annotated[str, Field(default="localhost")]
    QUEUE_PORT: Annotated[int, Field(default=6379)]

queue_settings: QueueSettings = QueueSettings()