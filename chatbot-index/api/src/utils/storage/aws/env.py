from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional, Annotated

class AWSStorageSettings(BaseSettings):
    s3_endpoint: Annotated[Optional[str], Field(default=None)]
    bucket_name: str
    aws_access_key_id: str
    aws_secret_access_key: str
    aws_region: str

aws_storage_settings: AWSStorageSettings = AWSStorageSettings()