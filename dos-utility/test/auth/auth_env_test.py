import pytest

from dos_utility.auth.env import AuthProvider, AuthSettings, get_auth_settings


@pytest.mark.parametrize("auth_provider", ["aws", "local"])
def test_get_auth_settings(monkeypatch: pytest.MonkeyPatch, auth_provider: str) -> None:
    """Test that auth settings can be loaded correctly."""
    get_auth_settings.cache_clear()

    monkeypatch.setenv("AUTH_PROVIDER", auth_provider)

    settings: AuthSettings = get_auth_settings()

    assert settings.AUTH_PROVIDER is AuthProvider(value=auth_provider)
