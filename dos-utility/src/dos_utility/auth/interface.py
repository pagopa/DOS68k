from abc import ABC, abstractmethod
from typing import Dict, Any


class AuthInterface(ABC):
    """Abstract base class for authentication providers.

    All concrete implementations must extend this class and implement its abstract methods.
    """

    @abstractmethod
    def get_jwks(self) -> Dict[str, Any]:
        """Retrieve the JSON Web Key Set (JWKS) from the authentication provider.

        Returns:
            Dict[str, Any]: The JWKS containing the public keys.

        Raises:
            HTTPException: If the JWKS endpoint is unreachable or returns an error.
        """
        ...

    @abstractmethod
    def verify_jwt(self, token: str) -> Dict[str, Any]:
        """Verify a JWT token and return its claims.

        Args:
            token: The JWT token to verify.

        Returns:
            Dict[str, Any]: The verified token claims.

        Raises:
            EmptyTokenException: If the token is an empty string.
            InvalidTokenKeyException: If the token's key ID is not found in the JWKS
                or the signature verification fails.
            TokenExpiredException: If the token has expired.
            InvalidTokenException: If the token is malformed or otherwise invalid.
        """
        ...
