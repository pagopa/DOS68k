import pytest

from fastapi import HTTPException
from dos_utility.auth.exceptions import TokenExpiredException, InvalidTokenKeyException

from src.modules.auth.service import AuthService, get_auth_service
from test.modules.auth.mocks import MockAuthProvider, MOCK_JWT_PAYLOAD


def test_get_auth_service_returns_instance():
    assert isinstance(get_auth_service(auth_interface=MockAuthProvider()), AuthService)


# ---------------------------------------------------------------------------
# valid token
# ---------------------------------------------------------------------------

def test_jwt_check_valid_bearer_token():
    """Valid 'Bearer <token>' header returns the provider claims."""
    result = AuthService(auth_interface=MockAuthProvider()).jwt_check(authorization="Bearer valid-token")

    assert result["status"] == "ok"
    assert result["payload"]["sub"] == MOCK_JWT_PAYLOAD["sub"]


# ---------------------------------------------------------------------------
# missing / malformed header → empty token → provider raises → 401
# ---------------------------------------------------------------------------

def test_jwt_check_no_auth_header():
    """Missing Authorization header falls back to empty token → 401."""
    with pytest.raises(HTTPException) as exc_info:
        AuthService(auth_interface=MockAuthProvider()).jwt_check(authorization=None)

    assert exc_info.value.status_code == 401


def test_jwt_check_no_bearer_prefix():
    """Header without 'Bearer ' prefix cannot be split → empty token → 401."""
    with pytest.raises(HTTPException) as exc_info:
        AuthService(auth_interface=MockAuthProvider()).jwt_check(authorization="token-without-prefix")

    assert exc_info.value.status_code == 401


# ---------------------------------------------------------------------------
# provider exceptions → all map to 401
# ---------------------------------------------------------------------------

def test_jwt_check_invalid_token():
    """Unknown token → InvalidTokenException from provider → 401."""
    with pytest.raises(HTTPException) as exc_info:
        AuthService(auth_interface=MockAuthProvider()).jwt_check(authorization="Bearer unknown-token")

    assert exc_info.value.status_code == 401


def test_jwt_check_expired_token():
    """Expired token → TokenExpiredException from provider → 401."""
    class ExpiredProvider(MockAuthProvider):
        def verify_jwt(self, token: str):
            raise TokenExpiredException()

    with pytest.raises(HTTPException) as exc_info:
        AuthService(auth_interface=ExpiredProvider()).jwt_check(authorization="Bearer expired-token")

    assert exc_info.value.status_code == 401


def test_jwt_check_invalid_key():
    """Invalid signing key → InvalidTokenKeyException from provider → 401."""
    class InvalidKeyProvider(MockAuthProvider):
        def verify_jwt(self, token: str):
            raise InvalidTokenKeyException()

    with pytest.raises(HTTPException) as exc_info:
        AuthService(auth_interface=InvalidKeyProvider()).jwt_check(authorization="Bearer some-token")

    assert exc_info.value.status_code == 401


def test_jwt_check_any_exception_becomes_401():
    """Any unexpected provider exception is mapped to 401, not 500."""
    class BrokenProvider(MockAuthProvider):
        def verify_jwt(self, token: str):
            raise RuntimeError("Unexpected failure")

    with pytest.raises(HTTPException) as exc_info:
        AuthService(auth_interface=BrokenProvider()).jwt_check(authorization="Bearer some-token")

    assert exc_info.value.status_code == 401
