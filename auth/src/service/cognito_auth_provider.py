"""
AWS Cognito implementation of the authentication provider.
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


class CognitoAuthProvider(BaseAuthProvider):
    """
    AWS Cognito implementation of the BaseAuthProvider.
    Handles JWT verification using AWS Cognito as the authentication provider.
    """

    def __init__(self):
        """Initialize the Cognito auth provider with settings."""
        self.region = SETTINGS.aws_cognito_region or SETTINGS.aws_region
        self.user_pool_id = SETTINGS.auth_cognito_userpool_id
        self.environment = SETTINGS.environment
        self.aws_endpoint_url = SETTINGS.aws_endpoint_url

    def get_jwks(self) -> Dict[str, Any]:
        """
        Retrieve the JWKS from AWS Cognito.
        
        Returns:
            Dict[str, Any]: The JWKS containing the public keys
            
        Raises:
            HTTPException: If the JWKS cannot be retrieved
        """
        # https://docs.getmoto.org/en/latest/docs/services/cognito-idp.html#cognito-idp
        if self.environment == "test":
            keys_url = (
                f"{self.aws_endpoint_url}/"
                f"{self.user_pool_id}/"
                ".well-known/jwks.json"
            )
            headers = {
                "Authorization": (
                    "AWS4-HMAC-SHA256 Credential=mock_access_key/20220524/"
                    f"{self.region}/cognito-idp/aws4_request, "
                    "SignedHeaders=content-length;content-type;host;x-amz-date, Signature=asdf"
                )
            }
        else:
            keys_url = (
                f"https://cognito-idp.{self.region}.amazonaws.com/"
                f"{self.user_pool_id}/"
                ".well-known/jwks.json"
            )
            headers = None

        response = requests.get(keys_url, headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            LOGGER.error(
                f"[CognitoAuthProvider.get_jwks] keys_url={keys_url}, "
                f"Response status code: {response.status_code}"
            )
            raise HTTPException(status_code=401, detail="Auth error")

    def verify_jwt(self, token: str) -> Dict[str, Any]:
        """
        Verify a JWT token using AWS Cognito's public keys.
        
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

            # since we passed the verification,
            # we can now safely use the unverified claims
            claims = jwt.get_unverified_claims(token)
            return claims
        except jwt_exceptions.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token has expired")
        except jwt_exceptions.JWTError as e:
            raise HTTPException(status_code=401, detail=f"Invalid token: {e}")
