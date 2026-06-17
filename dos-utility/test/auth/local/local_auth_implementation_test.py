import pytest
from uuid import UUID

from dos_utility.auth.local import LocalAuthProvider
from dos_utility.auth.local.implementation import LOCAL_USER_IDS
from dos_utility.auth import AuthInterface, UserRole
from dos_utility.auth.exceptions import InvalidTokenException


def test_local_provider_is_auth_interface():
    assert isinstance(LocalAuthProvider(), AuthInterface)


@pytest.mark.parametrize("role", [UserRole.ADMIN, UserRole.USER])
def test_local_provider_verify_jwt_returns_role_specific_claims(role):
    provider = LocalAuthProvider()
    claims = provider.verify_jwt(token=f"local-token-{role.value}")
    assert claims["role"] == role
    assert claims["sub"] == LOCAL_USER_IDS[role]
    # sub must be a valid UUID so X-User-Id header satisfies the UUID type
    UUID(claims["sub"])
    assert "iss" in claims
    assert "exp" in claims


def test_local_provider_verify_jwt_rejects_empty_token():
    provider = LocalAuthProvider()
    with pytest.raises(InvalidTokenException):
        provider.verify_jwt(token="")


def test_local_provider_verify_jwt_rejects_unknown_prefix():
    provider = LocalAuthProvider()
    with pytest.raises(InvalidTokenException):
        provider.verify_jwt(token="malformed-or-invalid-token")


def test_local_provider_verify_jwt_rejects_unknown_role():
    provider = LocalAuthProvider()
    with pytest.raises(InvalidTokenException):
        provider.verify_jwt(token="local-token-superuser")


def test_local_provider_get_jwks_returns_keys():
    provider = LocalAuthProvider()
    jwks = provider.get_jwks()
    assert "keys" in jwks
    assert isinstance(jwks["keys"], list)
    assert len(jwks["keys"]) > 0
