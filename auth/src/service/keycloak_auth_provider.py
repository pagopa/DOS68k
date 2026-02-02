"""
Keycloak implementation of the authentication provider.
This is a template/example implementation for Keycloak integration.
"""
import requests
from jose import jwk, jwt
from jose import exceptions as jwt_exceptions
from jose.utils import base64url_decode
from fastapi import HTTPException
from typing import Dict, Any

from .auth_provider_base import BaseAuthProvider
from src.modules.logger import get_logger
from src.modules.settings import SETTINGS

LOGGER = get_logger(__name__)


class KeycloakAuthProvider(BaseAuthProvider):
    """
    Keycloak implementation of the BaseAuthProvider.
    Handles JWT verification using Keycloak as the authentication provider.
    """

    def __init__(self):
        """Initialize the Keycloak auth provider with settings."""
        # These settings should be added to your environment configuration
        self.keycloak_url = getattr(SETTINGS, 'keycloak_url', None)
        self.keycloak_realm = getattr(SETTINGS, 'keycloak_realm', None)
        
        if not self.keycloak_url or not self.keycloak_realm:
            raise ValueError(
                "Keycloak configuration incomplete. "
                "Please set KEYCLOAK_URL and KEYCLOAK_REALM in environment."
            )

    def get_jwks(self) -> Dict[str, Any]:
        """
        Retrieve the JWKS from Keycloak.
        
        Returns:
            Dict[str, Any]: The JWKS containing the public keys
            
        Raises:
            HTTPException: If the JWKS cannot be retrieved
        """
        # Keycloak JWKS endpoint format:
        # {keycloak_url}/realms/{realm}/protocol/openid-connect/certs
        keys_url = (
            f"{self.keycloak_url}/realms/{self.keycloak_realm}/"
            "protocol/openid-connect/certs"
        )
        
        try:
            response = requests.get(keys_url, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                LOGGER.error(
                    f"[KeycloakAuthProvider.get_jwks] keys_url={keys_url}, "
                    f"Response status code: {response.status_code}"
                )
                raise HTTPException(status_code=401, detail="Auth error")
        except requests.RequestException as e:
            LOGGER.error(f"[KeycloakAuthProvider.get_jwks] Request failed: {e}")
            raise HTTPException(status_code=401, detail="Auth service unavailable")

    def verify_jwt(self, token: str) -> Dict[str, Any]:
        """
        Verify a JWT token using Keycloak's public keys.
        
        Args:
            token (str): The JWT token to verify
            
        Returns:
            Dict[str, Any]: The verified token claims
            
        Raises:
            HTTPException: If the token is invalid, expired, or verification fails
        """
        jwks = self.get_jwks()
        public_keys = {key["kid"]: key for key in jwks["keys"]}

        try:
            headers = jwt.get_unverified_header(token)
            kid = headers["kid"]
            if kid not in public_keys:
                raise HTTPException(status_code=401, detail="Invalid token key")

            public_key = jwk.construct(public_keys[kid])

            message, encoded_signature = str(token).rsplit(".", 1)
            decoded_signature = base64url_decode(encoded_signature.encode("utf-8"))
            if not public_key.verify(message.encode("utf8"), decoded_signature):
                raise HTTPException(status_code=401, detail="Error in public_key.verify")

            # Verify the token with additional checks
            claims = jwt.get_unverified_claims(token)
            
            # You can add additional Keycloak-specific validation here
            # For example, verify issuer matches expected Keycloak realm
            expected_issuer = f"{self.keycloak_url}/realms/{self.keycloak_realm}"
            if claims.get("iss") != expected_issuer:
                raise HTTPException(
                    status_code=401, 
                    detail=f"Invalid issuer. Expected {expected_issuer}"
                )
            
            return claims
        except jwt_exceptions.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token has expired")
        except jwt_exceptions.JWTError as e:
            raise HTTPException(status_code=401, detail=f"Invalid token: {e}")
