import pytest
from pydantic import ValidationError

from dos_utility.auth.env import AuthProvider, AuthSettings


def test_auth_provider_enum_values():
    assert AuthProvider.AWS == "aws"
    assert AuthProvider.LOCAL == "local"


def test_auth_settings_valid_aws(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("AUTH_PROVIDER", "aws")
    settings = AuthSettings()
    assert settings.AUTH_PROVIDER is AuthProvider.AWS


def test_auth_settings_valid_local(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("AUTH_PROVIDER", "local")
    settings = AuthSettings()
    assert settings.AUTH_PROVIDER is AuthProvider.LOCAL


def test_auth_settings_invalid_provider_raises(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("AUTH_PROVIDER", "unsupported")
    with pytest.raises(ValidationError):
        AuthSettings()


def test_auth_settings_missing_provider_raises(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("AUTH_PROVIDER", raising=False)
    with pytest.raises(ValidationError):
        AuthSettings()


def test_get_auth_settings(monkeypatch: pytest.MonkeyPatch):
    from dos_utility.auth.env import get_auth_settings

    get_auth_settings.cache_clear()

    monkeypatch.setenv("AUTH_PROVIDER", "aws")

    settings = get_auth_settings()

    assert settings.AUTH_PROVIDER is AuthProvider.AWS
