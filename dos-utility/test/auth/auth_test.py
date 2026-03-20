import pytest

from dos_utility.auth import get_auth, AuthInterface
from dos_utility.auth.env import AuthProvider
from dos_utility.auth.aws import CognitoAuthProvider
from dos_utility.auth.local import LocalAuthProvider


class _MockAWSSettings:
    AUTH_PROVIDER = AuthProvider.AWS


class _MockLocalSettings:
    AUTH_PROVIDER = AuthProvider.LOCAL


def test_get_auth_returns_cognito_provider(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr("dos_utility.auth.get_auth_settings", lambda: _MockAWSSettings())
    monkeypatch.setattr("dos_utility.auth.get_aws_auth_provider", lambda: CognitoAuthProvider.__new__(CognitoAuthProvider))

    result = get_auth()

    assert isinstance(result, CognitoAuthProvider)


def test_get_auth_returns_local_provider(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr("dos_utility.auth.get_auth_settings", lambda: _MockLocalSettings())

    result = get_auth()

    assert isinstance(result, LocalAuthProvider)


def test_get_auth_returns_auth_interface(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr("dos_utility.auth.get_auth_settings", lambda: _MockLocalSettings())

    result = get_auth()

    assert isinstance(result, AuthInterface)
