import logging
from typing import Dict, Any
from ..interface import AuthInterface

logger = logging.getLogger(__name__)


class LocalAuthProvider(AuthInterface):
    """
    Local/Mock implementation of the AuthInterface.
    Used for development and testing - always returns successful verification.
    """

    def __init__(self):
        """Initialize the local auth provider."""
        logger.warning("Using LocalAuthProvider - JWT verification is DISABLED")

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
        logger.info("Local auth provider - bypassing JWT verification")
        
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

def get_local_auth_provider() -> LocalAuthProvider:
    """Get an instance of the Local authentication provider."""
    return LocalAuthProvider()
