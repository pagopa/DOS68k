from .env import AuthProvider, AuthSettings, get_auth_settings
from .interface import AuthInterface
from .aws import get_aws_auth_provider
from .local import get_local_auth_provider


__all__ = ["AuthInterface", "get_auth_settings", "get_auth_provider"]

def get_auth_provider() -> AuthInterface:
    """Get the configured authentication provider instance."""
    auth_settings: AuthSettings = get_auth_settings() 
    
    if auth_settings.AUTH_PROVIDER is AuthProvider.AWS:
        return get_aws_auth_provider()
    elif auth_settings.AUTH_PROVIDER is AuthProvider.LOCAL:
        return get_local_auth_provider()
    else:
        raise ValueError(f"Unsupported AUTH_PROVIDER: {auth_settings.AUTH_PROVIDER}")
