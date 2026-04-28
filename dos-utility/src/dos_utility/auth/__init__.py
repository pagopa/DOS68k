from .env import AuthProvider, AuthSettings, get_auth_settings
from .interface import AuthInterface
from .aws import get_aws_auth_provider
from .local import get_local_auth_provider
from .exceptions import (
    EmptyTokenException,
    TokenExpiredException,
    InvalidTokenException,
    InvalidTokenKeyException,
)
from .dependency import get_user, get_admin_user, User, UserRole


__all__ = [
    "AuthInterface",
    "get_auth",
    "EmptyTokenException",
    "TokenExpiredException",
    "InvalidTokenException",
    "InvalidTokenKeyException",
    "get_user",
    "get_admin_user",
    "User",
    "UserRole",
]


def get_auth() -> AuthInterface:
    """Get the configured authentication provider instance."""
    auth_settings: AuthSettings = get_auth_settings()

    if auth_settings.AUTH_PROVIDER is AuthProvider.AWS:
        return get_aws_auth_provider()
    elif auth_settings.AUTH_PROVIDER is AuthProvider.LOCAL:
        return get_local_auth_provider()
