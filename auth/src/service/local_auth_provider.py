"""
Local authentication provider for development/testing.
Bypasses actual JWT verification and returns mock claims.
"""
from typing import Dict, Any
from .auth_provider_base import BaseAuthProvider
from src.modules.logger import get_logger

LOGGER = get_logger(__name__)


class LocalAuthProvider(BaseAuthProvider):
    """
    Local/Mock implementation of the BaseAuthProvider.
    Used for development and testing - always returns successful verification.
    """

    def __init__(self):
        """Initialize the local auth provider."""
        LOGGER.warning("Using LocalAuthProvider - JWT verification is DISABLED")

    def get_jwks(self) -> Dict[str, Any]:
        """
        Return mock JWKS for local development.
        
        Returns:
            Dict[str, Any]: Mock JWKS
        """
        return {
            "keys": [
                {
                    "kid": "local-mock-key",
                    "kty": "RSA",
                    "use": "sig",
                    "n": "mock-modulus",
                    "e": "AQAB"
                }
            ]
        }

    def verify_jwt(self, token: str) -> Dict[str, Any]:
        """
        Mock JWT verification - always succeeds.
        Returns mock claims without actual token verification.
        
        Args:
            token (str): The JWT token (ignored in local mode)
            
        Returns:
            Dict[str, Any]: Mock token claims
        """
        LOGGER.info("Local auth provider - bypassing JWT verification")
        
        # Return mock claims that simulate a valid token
        return {
            "sub": "local-user-123",
            "email": "local@example.com",
            "name": "Local Development User",
            "cognito:username": "localuser",
            "exp": 9999999999,  # Far future expiration
            "iat": 1000000000,
            "auth_time": 1000000000,
            "token_use": "access",
            "iss": "https://local-development",
            "client_id": "local-client"
        }
