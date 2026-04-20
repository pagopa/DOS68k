from typing import Dict, Any, Optional, Self
from fastapi import HTTPException, status
from dos_utility.auth import AuthInterface
from dos_utility.auth.exceptions import EmptyTokenException, InvalidTokenException


MOCK_JWT_PAYLOAD: Dict[str, Any] = {
    "sub": "test-user-123",
    "iss": "https://test-issuer.example.com",
    "exp": 9999999999,
    "iat": 1000000000,
    "email": "test@example.com",
}


# ---------------------------------------------------------------------------
# Auth provider mocks
# ---------------------------------------------------------------------------

class MockAuthProvider(AuthInterface):
    """Mock auth provider.

    - 'valid-token' and 'mock-token' → return MOCK_JWT_PAYLOAD
    - empty string → raise EmptyTokenException
    - anything else → raise InvalidTokenException
    """

    def get_jwks(self: Self) -> Dict[str, Any]:
        return {"keys": []}

    def verify_jwt(self: Self, token: str) -> Dict[str, Any]:
        if token in ("valid-token", "mock-token"):
            return MOCK_JWT_PAYLOAD
        if token == "":
            raise EmptyTokenException()
        raise InvalidTokenException()


# ---------------------------------------------------------------------------
# Service mocks for controller tests (dependency override pattern)
# ---------------------------------------------------------------------------

def get_auth_service_200_mock():
    class AuthServiceMock:
        def jwt_check(self, authorization: Optional[str]) -> Dict[str, Any]:
            return {"status": "ok", "payload": MOCK_JWT_PAYLOAD}

    return AuthServiceMock()


def get_auth_service_401_mock():
    class AuthServiceMock:
        def jwt_check(self, authorization: Optional[str]) -> Dict[str, Any]:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized user")

    return AuthServiceMock()


def get_auth_service_500_mock():
    class AuthServiceMock:
        def jwt_check(self, authorization: Optional[str]) -> Dict[str, Any]:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

    return AuthServiceMock()
