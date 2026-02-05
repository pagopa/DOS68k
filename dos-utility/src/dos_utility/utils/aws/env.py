from functools import lru_cache
from pydantic_settings import BaseSettings
from pydantic import Field, SecretStr

class AWSCredentialsSettings(BaseSettings):
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: SecretStr

@lru_cache
def get_aws_credentials_settings() -> AWSCredentialsSettings:
    return AWSCredentialsSettings()
