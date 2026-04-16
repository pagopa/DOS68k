import requests

from logging import Logger
from jose import jwk, jwt
from jose import exceptions as jwt_exceptions
from jose.utils import base64url_decode
from fastapi import HTTPException
from typing import Dict, Any, Self

from .env import AWSAuthSettings, get_aws_auth_settings
from ..exceptions import EmptyTokenException, InvalidTokenKeyException, InvalidTokenException, TokenExpiredException
from ..interface import AuthInterface
from ...utils.logger import get_logger




class CognitoAuthProvider(AuthInterface):
    def __init__(self: Self):
        self.logger: Logger = get_logger(name=__name__)
        self.__settings: AWSAuthSettings = get_aws_auth_settings()
        self.region = self.__settings.AWS_REGION
        self.aws_endpoint_url = self.__settings.AWS_ENDPOINT_URL
        self.access_key_id = self.__settings.AWS_ACCESS_KEY_ID
        self.secret_access_key = self.__settings.AWS_SECRET_ACCESS_KEY.get_secret_value()
        self.user_pool_id = self.__settings.AWS_COGNITO_USERPOOL_ID
        self.environment = self.__settings.ENVIRONMENT

    def get_jwks(self: Self) -> Dict[str, Any]:
        """Retrieve the JWKS from AWS Cognito.

        Returns:
            Dict[str, Any]: The JWKS containing the public keys.

        Raises:
            HTTPException: If the JWKS endpoint returns a non-200 response.
        """
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
            self.logger.error(
                f"[CognitoAuthProvider.get_jwks] keys_url={keys_url}, "
                f"Response status code: {response.status_code}"
            )

            raise HTTPException(status_code=401, detail="Auth error")

    def verify_jwt(self: Self, token: str) -> Dict[str, Any]:
        """Verify a JWT token using AWS Cognito's public keys.

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
        if token == "":
            raise EmptyTokenException

        jwks = self.get_jwks()
        public_keys = {key["kid"]: key for key in jwks["keys"]}

        try:
            headers = jwt.get_unverified_header(token)
            kid = headers["kid"]

            if kid not in public_keys:
                raise InvalidTokenKeyException

            public_key = jwk.construct(public_keys[kid])
            message, encoded_signature = str(token).rsplit(".", 1)
            decoded_signature = base64url_decode(encoded_signature.encode("utf-8"))

            if not public_key.verify(message.encode("utf8"), decoded_signature):
                raise InvalidTokenKeyException

            # since we passed the verification,
            # we can now safely use the unverified claims
            claims = jwt.get_unverified_claims(token)
        except jwt_exceptions.ExpiredSignatureError:
            raise TokenExpiredException
        except jwt_exceptions.JWTError as e:
            raise InvalidTokenException

        return claims


def get_aws_auth_provider() -> CognitoAuthProvider:
    """Get an instance of the AWS Cognito authentication provider."""
    return CognitoAuthProvider()