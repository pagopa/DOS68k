from functools import lru_cache
from pydantic_settings import BaseSettings
from pydantic import Field
from enum import StrEnum

class QueueProvider(StrEnum):
    REDIS = "redis"
    SQS = "sqs"

class QueueSettings(BaseSettings):
    QUEUE_PROVIDER: QueueProvider


@lru_cache()
def get_queue_settings() -> QueueSettings:
    return QueueSettings()