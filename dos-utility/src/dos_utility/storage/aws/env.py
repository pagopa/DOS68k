from functools import lru_cache
from pydantic_settings import BaseSettings
from pydantic import SecretStr

class AWSStorageSettings(BaseSettings):
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: SecretStr
    AWS_REGION: str

@lru_cache
def get_aws_storage_settings() -> AWSStorageSettings:
    return AWSStorageSettings()
