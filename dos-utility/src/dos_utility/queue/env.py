from functools import lru_cache
from pydantic_settings import BaseSettings
from pydantic import Field
from enum import StrEnum

class QueueType(StrEnum):
    REDIS = "redis"
    SQS = "sqs"

class QueueSettings(BaseSettings):
    queue_type: QueueType


@lru_cache()
def get_queue_settings() -> QueueSettings:
    return QueueSettings()