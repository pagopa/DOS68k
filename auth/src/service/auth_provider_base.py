"""
Abstract base class for authentication providers.
Implements the Strategy pattern to allow different JWT authentication providers.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseAuthProvider(ABC):
    """
    Abstract base class for authentication providers.
    All concrete implementations must extend this class and implement its abstract methods.
    """

    @abstractmethod
    def get_jwks(self) -> Dict[str, Any]:
        """
        Retrieve the JSON Web Key Set (JWKS) from the authentication provider.
        
        Returns:
            Dict[str, Any]: The JWKS containing the public keys
            
        Raises:
            HTTPException: If the JWKS cannot be retrieved
        """
        pass

    @abstractmethod
    def verify_jwt(self, token: str) -> Dict[str, Any]:
        """
        Verify a JWT token and return its claims.
        
        Args:
            token (str): The JWT token to verify
            
        Returns:
            Dict[str, Any]: The verified token claims
            
        Raises:
            HTTPException: If the token is invalid, expired, or verification fails
        """
        pass
