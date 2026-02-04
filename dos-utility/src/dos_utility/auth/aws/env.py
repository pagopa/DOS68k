from functools import lru_cache
from pydantic_settings import BaseSettings
from pydantic import SecretStr

class AWSAuthSettings(BaseSettings):
    AWS_REGION: str
    AWS_ENDPOINT_URL: str
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: SecretStr
    AWS_COGNITO_USERPOOL_ID: str
    ENVIRONMENT: str = "dev"

@lru_cache()
def get_aws_auth_settings() -> AWSAuthSettings:
    return AWSAuthSettings()