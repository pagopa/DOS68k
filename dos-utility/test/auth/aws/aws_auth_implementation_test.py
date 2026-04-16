import pytest
from unittest.mock import MagicMock
from fastapi import HTTPException

from dos_utility.auth.aws.implementation import CognitoAuthProvider
from dos_utility.auth.exceptions import (
    EmptyTokenException,
    InvalidTokenKeyException,
    TokenExpiredException,
    InvalidTokenException,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

class _MockSecretStr:
    def get_secret_value(self):
        return "test-secret"


class _MockAWSSettings:
    AWS_REGION = "us-east-1"
    AWS_ENDPOINT_URL = "http://localhost:4566"
    AWS_ACCESS_KEY_ID = "test-key"
    AWS_SECRET_ACCESS_KEY = _MockSecretStr()
    AWS_COGNITO_USERPOOL_ID = "us-east-1_TestPool"
    ENVIRONMENT = "test"


class _MockAWSSettingsProd(_MockAWSSettings):
    ENVIRONMENT = "dev"


@pytest.fixture
def provider(monkeypatch: pytest.MonkeyPatch) -> CognitoAuthProvider:
    monkeypatch.setattr(
        "dos_utility.auth.aws.implementation.get_aws_auth_settings",
        lambda: _MockAWSSettings(),
    )
    return CognitoAuthProvider()


@pytest.fixture
def provider_prod(monkeypatch: pytest.MonkeyPatch) -> CognitoAuthProvider:
    monkeypatch.setattr(
        "dos_utility.auth.aws.implementation.get_aws_auth_settings",
        lambda: _MockAWSSettingsProd(),
    )
    return CognitoAuthProvider()


# ---------------------------------------------------------------------------
# get_jwks
# ---------------------------------------------------------------------------

def test_get_jwks_test_env_uses_endpoint_url(monkeypatch: pytest.MonkeyPatch, provider: CognitoAuthProvider):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"keys": [{"kid": "test-kid"}]}

    captured_url = {}

    def mock_get(url, headers=None):
        captured_url["url"] = url
        return mock_response

    monkeypatch.setattr("dos_utility.auth.aws.implementation.requests.get", mock_get)

    result = provider.get_jwks()

    assert "localhost:4566" in captured_url["url"]
    assert result == {"keys": [{"kid": "test-kid"}]}


def test_get_jwks_prod_env_uses_cognito_url(monkeypatch: pytest.MonkeyPatch, provider_prod: CognitoAuthProvider):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"keys": []}

    captured_url = {}

    def mock_get(url, headers=None):
        captured_url["url"] = url
        return mock_response

    monkeypatch.setattr("dos_utility.auth.aws.implementation.requests.get", mock_get)

    provider_prod.get_jwks()

    assert "cognito-idp" in captured_url["url"]
    assert "amazonaws.com" in captured_url["url"]


def test_get_jwks_non_200_raises_http_exception(monkeypatch: pytest.MonkeyPatch, provider: CognitoAuthProvider):
    mock_response = MagicMock()
    mock_response.status_code = 403

    monkeypatch.setattr(
        "dos_utility.auth.aws.implementation.requests.get",
        lambda url, headers=None: mock_response,
    )

    with pytest.raises(HTTPException) as exc_info:
        provider.get_jwks()

    assert exc_info.value.status_code == 401


# ---------------------------------------------------------------------------
# verify_jwt
# ---------------------------------------------------------------------------

def test_verify_jwt_empty_token_raises(provider: CognitoAuthProvider):
    with pytest.raises(EmptyTokenException):
        provider.verify_jwt(token="")


def test_verify_jwt_unknown_kid_raises(monkeypatch: pytest.MonkeyPatch, provider: CognitoAuthProvider):
    monkeypatch.setattr(
        provider,
        "get_jwks",
        lambda: {"keys": [{"kid": "known-kid", "kty": "RSA"}]},
    )
    monkeypatch.setattr(
        "dos_utility.auth.aws.implementation.jwt.get_unverified_header",
        lambda token: {"kid": "unknown-kid"},
    )

    with pytest.raises(InvalidTokenKeyException):
        provider.verify_jwt(token="header.payload.signature")


def test_verify_jwt_invalid_signature_raises(monkeypatch: pytest.MonkeyPatch, provider: CognitoAuthProvider):
    mock_key = MagicMock()
    mock_key.verify.return_value = False

    monkeypatch.setattr(
        provider,
        "get_jwks",
        lambda: {"keys": [{"kid": "test-kid", "kty": "RSA"}]},
    )
    monkeypatch.setattr(
        "dos_utility.auth.aws.implementation.jwt.get_unverified_header",
        lambda token: {"kid": "test-kid"},
    )
    monkeypatch.setattr(
        "dos_utility.auth.aws.implementation.jwk.construct",
        lambda key: mock_key,
    )
    monkeypatch.setattr(
        "dos_utility.auth.aws.implementation.base64url_decode",
        lambda s: b"decoded-sig",
    )

    with pytest.raises(InvalidTokenKeyException):
        provider.verify_jwt(token="header.payload.signature")


def test_verify_jwt_expired_token_raises(monkeypatch: pytest.MonkeyPatch, provider: CognitoAuthProvider):
    from jose import exceptions as jwt_exceptions

    mock_key = MagicMock()
    mock_key.verify.return_value = True

    monkeypatch.setattr(
        provider,
        "get_jwks",
        lambda: {"keys": [{"kid": "test-kid", "kty": "RSA"}]},
    )
    monkeypatch.setattr(
        "dos_utility.auth.aws.implementation.jwt.get_unverified_header",
        lambda token: {"kid": "test-kid"},
    )
    monkeypatch.setattr(
        "dos_utility.auth.aws.implementation.jwk.construct",
        lambda key: mock_key,
    )
    monkeypatch.setattr(
        "dos_utility.auth.aws.implementation.base64url_decode",
        lambda s: b"decoded-sig",
    )
    monkeypatch.setattr(
        "dos_utility.auth.aws.implementation.jwt.get_unverified_claims",
        lambda token: (_ for _ in ()).throw(jwt_exceptions.ExpiredSignatureError()),
    )

    with pytest.raises(TokenExpiredException):
        provider.verify_jwt(token="header.payload.signature")


def test_verify_jwt_malformed_token_raises(monkeypatch: pytest.MonkeyPatch, provider: CognitoAuthProvider):
    from jose import exceptions as jwt_exceptions

    monkeypatch.setattr(
        provider,
        "get_jwks",
        lambda: {"keys": [{"kid": "test-kid", "kty": "RSA"}]},
    )
    monkeypatch.setattr(
        "dos_utility.auth.aws.implementation.jwt.get_unverified_header",
        lambda token: (_ for _ in ()).throw(jwt_exceptions.JWTError("malformed")),
    )

    with pytest.raises(InvalidTokenException):
        provider.verify_jwt(token="header.payload.signature")


def test_verify_jwt_valid_token_returns_claims(monkeypatch: pytest.MonkeyPatch, provider: CognitoAuthProvider):
    mock_claims = {"sub": "user-123", "email": "user@example.com", "exp": 9999999999}
    mock_key = MagicMock()
    mock_key.verify.return_value = True

    monkeypatch.setattr(
        provider,
        "get_jwks",
        lambda: {"keys": [{"kid": "test-kid", "kty": "RSA"}]},
    )
    monkeypatch.setattr(
        "dos_utility.auth.aws.implementation.jwt.get_unverified_header",
        lambda token: {"kid": "test-kid"},
    )
    monkeypatch.setattr(
        "dos_utility.auth.aws.implementation.jwk.construct",
        lambda key: mock_key,
    )
    monkeypatch.setattr(
        "dos_utility.auth.aws.implementation.base64url_decode",
        lambda s: b"decoded-sig",
    )
    monkeypatch.setattr(
        "dos_utility.auth.aws.implementation.jwt.get_unverified_claims",
        lambda token: mock_claims,
    )

    result = provider.verify_jwt(token="header.payload.signature")

    assert result == mock_claims


def test_get_aws_auth_provider(monkeypatch: pytest.MonkeyPatch):
    from dos_utility.auth.aws.implementation import get_aws_auth_provider

    monkeypatch.setattr(
        "dos_utility.auth.aws.implementation.get_aws_auth_settings",
        lambda: _MockAWSSettings(),
    )

    provider = get_aws_auth_provider()

    assert isinstance(provider, CognitoAuthProvider)
