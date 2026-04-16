from typing import Optional, Dict, Any, Self, Annotated
from fastapi import HTTPException, status, Depends
from logging import Logger
from dos_utility.auth import get_auth, AuthInterface
from dos_utility.utils.logger import get_logger

LOGGER: Logger = get_logger(name=__name__)


class AuthService:
    def __init__(self: Self, auth_interface: AuthInterface):
        self.__auth: AuthInterface = auth_interface

    def jwt_check(self: Self, authorization: Optional[str]) -> Dict[str, Any]:
        """Verify a JWT token using the configured authentication provider.

        Args:
            authorization: Value of the Authorization header, or None if absent.

        Returns:
            Dict with keys: status, payload.

        Raises:
            HTTPException: 401 if the token is missing or malformed, 500 on unexpected errors.
        """
        try:
            token: str = authorization.split(" ", 1)[1]
        except Exception:
            token: str = "" # Set to empty string, so that we can make the call anyway. If the provider is local then everything is ok since there is a mock, otherwise an error will be raised

        try:
            payload: Dict[str, Any] = self.__auth.verify_jwt(token=token)
        except Exception:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized user")

        return {"status": "ok", "payload": payload}

def get_auth_service(auth_interface: Annotated[AuthInterface, Depends(dependency=get_auth)]) -> AuthService:
    return AuthService(auth_interface=auth_interface)
