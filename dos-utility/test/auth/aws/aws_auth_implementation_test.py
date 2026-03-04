import pytest
from typing import Dict, Any

from dos_utility.auth.aws import implementation, CognitoAuthProvider, get_aws_auth_provider
from dos_utility.auth.aws.env import get_aws_auth_settings

from test.auth.aws.mocks import (
    requests_mock,
    requests_unhealthy_mock,
    get_aws_auth_settings_mock,
)


def test_instantiate_cognito_auth_provider(monkeypatch: pytest.MonkeyPatch):
    """Test that CognitoAuthProvider can be instantiated."""
    get_aws_auth_settings.cache_clear()

    monkeypatch.setattr(implementation, "get_aws_auth_settings", get_aws_auth_settings_mock)

    provider: CognitoAuthProvider = CognitoAuthProvider()

    assert isinstance(provider, CognitoAuthProvider)
    assert provider.region == "us-east-1"
    assert provider.user_pool_id == "us-east-1_MockPoolId"


def test_get_aws_auth_provider(monkeypatch: pytest.MonkeyPatch):
    """Test get_aws_auth_provider factory function."""
    get_aws_auth_settings.cache_clear()

    monkeypatch.setattr(implementation, "get_aws_auth_settings", get_aws_auth_settings_mock)

    provider: CognitoAuthProvider = get_aws_auth_provider()

    assert isinstance(provider, CognitoAuthProvider)


def test_cognito_get_jwks(monkeypatch: pytest.MonkeyPatch):
    """Test that get_jwks retrieves JWKS successfully."""
    get_aws_auth_settings.cache_clear()

    monkeypatch.setattr(implementation, "get_aws_auth_settings", get_aws_auth_settings_mock)
    monkeypatch.setattr(implementation, "requests", requests_mock())

    provider: CognitoAuthProvider = CognitoAuthProvider()
    jwks: Dict[str, Any] = provider.get_jwks()

    assert isinstance(jwks, dict)
    assert "keys" in jwks
    assert isinstance(jwks["keys"], list)
    assert len(jwks["keys"]) > 0


def test_cognito_get_jwks_failure(monkeypatch: pytest.MonkeyPatch):
    """Test that get_jwks raises HTTPException on failure."""
    get_aws_auth_settings.cache_clear()

    monkeypatch.setattr(implementation, "get_aws_auth_settings", get_aws_auth_settings_mock)
    monkeypatch.setattr(implementation, "requests", requests_unhealthy_mock())

    provider: CognitoAuthProvider = CognitoAuthProvider()
    
    with pytest.raises(Exception):
        provider.get_jwks()


def test_cognito_verify_jwt_invalid_token(monkeypatch: pytest.MonkeyPatch):
    """Test that verify_jwt handles invalid tokens correctly."""
    get_aws_auth_settings.cache_clear()

    monkeypatch.setattr(implementation, "get_aws_auth_settings", get_aws_auth_settings_mock)
    monkeypatch.setattr(implementation, "requests", requests_mock())

    provider: CognitoAuthProvider = CognitoAuthProvider()
    
    # Test with an invalid token format
    with pytest.raises(Exception):
        provider.verify_jwt("invalid.token.format")
