from functools import lru_cache
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Annotated, Optional


class DynamoDBSettings(BaseSettings):
    DYNAMODB_REGION: Annotated[str, Field(default="us-east-1")]
    DYNAMODB_ENDPOINT_URL: Annotated[Optional[str], Field(default=None)]
    DYNAMODB_PORT: Annotated[Optional[int], Field(default=None)]
    DYNAMODB_TABLE_PREFIX: Annotated[Optional[str], Field(default=None)]


@lru_cache
def get_dynamodb_settings() -> DynamoDBSettings:
    return DynamoDBSettings()
