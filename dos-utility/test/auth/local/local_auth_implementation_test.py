import pytest
from typing import Dict, Any

from dos_utility.auth.local import LocalAuthProvider, get_local_auth_provider


def test_instantiate_local_auth_provider():
    """Test that LocalAuthProvider can be instantiated."""
    provider: LocalAuthProvider = LocalAuthProvider()

    assert isinstance(provider, LocalAuthProvider)


def test_get_local_auth_provider():
    """Test get_local_auth_provider factory function."""
    provider: LocalAuthProvider = get_local_auth_provider()

    assert isinstance(provider, LocalAuthProvider)


def test_local_get_jwks():
    """Test that get_jwks returns mock JWKS."""
    provider: LocalAuthProvider = LocalAuthProvider()
    jwks: Dict[str, Any] = provider.get_jwks()

    assert isinstance(jwks, dict)
    assert "keys" in jwks
    assert isinstance(jwks["keys"], list)
    assert len(jwks["keys"]) > 0
    assert jwks["keys"][0]["kid"] == "local-mock-key"


def test_local_verify_jwt():
    """Test that verify_jwt returns mock claims without verification."""
    provider: LocalAuthProvider = LocalAuthProvider()
    
    # LocalAuthProvider should accept any token and return mock claims
    claims: Dict[str, Any] = provider.verify_jwt("any.token.value")

    assert isinstance(claims, dict)
    assert "sub" in claims
    assert "email" in claims


def test_local_verify_jwt_no_actual_verification():
    """Test that LocalAuthProvider doesn't perform actual JWT verification."""
    provider: LocalAuthProvider = LocalAuthProvider()
    
    # Should work with completely invalid tokens since it's a mock
    invalid_token = "not-a-valid-jwt"
    claims: Dict[str, Any] = provider.verify_jwt(invalid_token)

    assert isinstance(claims, dict)
    # Verify that it returns mock data regardless of token validity
    assert claims["sub"] == "local-user-123"
