from functools import lru_cache
from pydantic_settings import BaseSettings
from pydantic import SecretStr


class MinIOStorageSettings(BaseSettings):
    MINIO_ENDPOINT: str
    MINIO_PORT: int
    MINIO_ACCESS_KEY: str
    MINIO_SECRET_KEY: SecretStr
    MINIO_REGION: str

@lru_cache()
def get_minio_storage_settings() -> MinIOStorageSettings:
    return MinIOStorageSettings()