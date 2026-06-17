from logging import Logger
from typing import Dict, Any

from ..interface import AuthInterface
from ..dependency import UserRole
from ..exceptions import InvalidTokenException
from ...utils.logger import get_logger


LOCAL_USER_IDS: Dict[UserRole, str] = {
    UserRole.USER: "00000000-0000-0000-0000-000000000001",
    UserRole.ADMIN: "00000000-0000-0000-0000-000000000002",
}

_TOKEN_PREFIX = "local-token-"


class LocalAuthProvider(AuthInterface):
    """
    Local/Mock implementation of the AuthInterface.
    Parses dev tokens of the form `local-token-<role>` and returns matching
    mock claims. Any other token is rejected so that 401 propagation through
    the gateway can be exercised in local-dev.
    """

    def __init__(self):
        self.logger: Logger = get_logger(name=__name__)
        self.logger.warning("Using LocalAuthProvider - JWT verification is DISABLED")

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
                    "e": "AQAB",
                }
            ]
        }

    def verify_jwt(self, token: str) -> Dict[str, Any]:
        """
        Mock JWT verification.

        Accepts tokens of the form `local-token-<role>` where <role> is one of
        the UserRole values. Returns mock claims with `sub` set to a stable
        UUID for that role and `role` set to the role itself.

        Args:
            token (str): The dev token to parse.

        Returns:
            Dict[str, Any]: Mock token claims.

        Raises:
            InvalidTokenException: If the token doesn't match `local-token-<role>`.
        """
        if not token or not token.startswith(_TOKEN_PREFIX):
            self.logger.info("Local auth provider - rejecting non-dev token")
            raise InvalidTokenException(
                msg="Local provider only accepts local-token-<role>"
            )

        role_value = token[len(_TOKEN_PREFIX) :]
        try:
            role = UserRole(role_value)
        except ValueError:
            self.logger.info("Local auth provider - unknown role in token")
            raise InvalidTokenException(msg=f"Unknown role: {role_value}")

        self.logger.info(
            "Local auth provider - issuing mock claims for role %s", role.value
        )

        return {
            "sub": LOCAL_USER_IDS[role],
            "email": f"{role.value}@local.example.com",
            "name": f"Local {role.value.capitalize()} User",
            "cognito:username": f"local-{role.value}",
            "exp": 9999999999,
            "iat": 1000000000,
            "auth_time": 1000000000,
            "token_use": "access",
            "iss": "https://local-development",
            "client_id": "local-client",
            "role": role,
        }


def get_local_auth_provider() -> LocalAuthProvider:
    """Get an instance of the Local authentication provider."""
    return LocalAuthProvider()
