from functools import lru_cache
from typing import Annotated, Optional
from pydantic_settings import BaseSettings
from pydantic import SecretStr, Field

class AWSCredentialsSettings(BaseSettings):
    AWS_ACCESS_KEY_ID: Annotated[Optional[str], Field(default=None)]
    AWS_SECRET_ACCESS_KEY: Annotated[Optional[SecretStr], Field(default=None)]

@lru_cache
def get_aws_credentials_settings() -> AWSCredentialsSettings:
    return AWSCredentialsSettings()
