from functools import lru_cache
from pydantic_settings import BaseSettings
from pydantic import Field, SecretStr
from typing import Annotated

class SQSQueueSettings(BaseSettings):
    SQS_ENDPOINT_URL: Annotated[str, Field(default="http://localhost")]
    SQS_PORT: Annotated[int, Field(default=4566)]
    SQS_REGION: Annotated[str, Field(default="us-east-1")]
    AWS_ACCESS_KEY_ID: Annotated[str, Field(default="test")]
    AWS_SECRET_ACCESS_KEY: Annotated[SecretStr, Field(default=SecretStr("test"))]
    SQS_QUEUE_NAME: str
    SQS_QUEUE_URL: str

@lru_cache
def get_sqs_queue_settings() -> SQSQueueSettings:
    return SQSQueueSettings()