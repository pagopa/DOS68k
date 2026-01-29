from functools import lru_cache
from pydantic_settings import BaseSettings
from enum import StrEnum


class StorageProvider(StrEnum):
    AWS_S3 = "aws_s3"
    MINIO = "minio"

class StorageSettings(BaseSettings):
    STORAGE_PROVIDER: StorageProvider


@lru_cache
def get_storage_settings() -> StorageSettings:
    return StorageSettings()