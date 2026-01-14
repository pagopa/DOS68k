from typing import Annotated
from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    frontend_url: Annotated[str, Field(default="http://localhost")]

class DBSettings(BaseSettings):
    DB_USERNAME: Annotated[str, Field(default="postgres")]
    DB_PASSWORD: Annotated[SecretStr, Field(default="password")]
    DB_HOST: Annotated[str, Field(default="localhost")]
    DB_PORT: Annotated[int, Field(default=5432)]
    DB_NAME: Annotated[str, Field(default="db")]

class QueueSettings(BaseSettings):
    QUEUE_HOST: Annotated[str, Field(default="localhost")]
    QUEUE_PORT: Annotated[int, Field(default=6379)]

settings: Settings = Settings()
db_settings: DBSettings = DBSettings()
queue_settings: QueueSettings = QueueSettings()