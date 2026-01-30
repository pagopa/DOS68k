from functools import lru_cache
from typing import Annotated, Optional
from pydantic_settings import BaseSettings
from pydantic import SecretStr, Field

class AWSStorageSettings(BaseSettings):
    S3_ENDPOINT: Annotated[Optional[str], Field(default=None)]
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: SecretStr
    AWS_REGION: str

@lru_cache
def get_aws_storage_settings() -> AWSStorageSettings:
    return AWSStorageSettings()
