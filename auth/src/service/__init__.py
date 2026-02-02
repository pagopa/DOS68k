"""Service package for authentication."""
from .auth_provider_base import BaseAuthProvider
from .cognito_auth_provider import CognitoAuthProvider
from .keycloak_auth_provider import KeycloakAuthProvider
from .local_auth_provider import LocalAuthProvider
from src.modules.settings import SETTINGS


def get_provider() -> BaseAuthProvider:
    """Get the configured authentication provider instance."""
    provider_type = SETTINGS.auth_provider.lower()
    if provider_type == "cognito":
        return CognitoAuthProvider()
    elif provider_type == "keycloak":
        return KeycloakAuthProvider()
    elif provider_type == "local":
        return LocalAuthProvider()
    else:
        raise ValueError(f"Unsupported auth provider: {provider_type}")


__all__ = [
    "BaseAuthProvider",
    "CognitoAuthProvider",
    "KeycloakAuthProvider",
    "LocalAuthProvider",
    "get_provider",
]
