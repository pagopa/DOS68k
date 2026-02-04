from pydantic_settings import BaseSettings
from functools import lru_cache
from enum import StrEnum

class AuthProvider(StrEnum):
    AWS = "aws"
    KEYCLOAK = "keycloak"
    LOCAL = "local"

class AuthSettings(BaseSettings):
    AUTH_PROVIDER: AuthProvider

@lru_cache()
def get_auth_settings() -> AuthSettings:
    return AuthSettings()