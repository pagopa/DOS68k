from dos_utility.auth.local import LocalAuthProvider
from dos_utility.auth import AuthInterface


def test_local_provider_is_auth_interface():
    assert isinstance(LocalAuthProvider(), AuthInterface)


def test_local_provider_verify_jwt_returns_claims():
    provider = LocalAuthProvider()
    claims = provider.verify_jwt(token="any-token")
    assert "sub" in claims
    assert "iss" in claims
    assert "exp" in claims


def test_local_provider_verify_jwt_accepts_empty_token():
    """Local provider bypasses verification and always succeeds, even with an empty token."""
    provider = LocalAuthProvider()
    claims = provider.verify_jwt(token="")
    assert "sub" in claims


def test_local_provider_verify_jwt_accepts_any_token():
    provider = LocalAuthProvider()
    claims = provider.verify_jwt(token="malformed-or-invalid-token")
    assert "sub" in claims


def test_local_provider_get_jwks_returns_keys():
    provider = LocalAuthProvider()
    jwks = provider.get_jwks()
    assert "keys" in jwks
    assert isinstance(jwks["keys"], list)
    assert len(jwks["keys"]) > 0
