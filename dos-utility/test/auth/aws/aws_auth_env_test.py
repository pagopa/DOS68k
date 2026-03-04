import pytest

from pydantic import SecretStr

from dos_utility.auth.aws.env import AWSAuthSettings, get_aws_auth_settings


def test_get_aws_auth_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that AWS auth settings can be loaded correctly."""
    get_aws_auth_settings.cache_clear()

    monkeypatch.setenv("AWS_REGION", "us-east-1")
    monkeypatch.setenv("AWS_ENDPOINT_URL", "http://localhost:9229")
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "test-access-key")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "test-secret-key")
    monkeypatch.setenv("AWS_COGNITO_USERPOOL_ID", "us-east-1_TestPool")
    monkeypatch.setenv("ENVIRONMENT", "test")

    settings: AWSAuthSettings = get_aws_auth_settings()

    assert settings.AWS_REGION == "us-east-1"
    assert settings.AWS_ENDPOINT_URL == "http://localhost:9229"
    assert settings.AWS_ACCESS_KEY_ID == "test-access-key"
    assert isinstance(settings.AWS_SECRET_ACCESS_KEY, SecretStr)
    assert settings.AWS_SECRET_ACCESS_KEY.get_secret_value() == "test-secret-key"
    assert settings.AWS_COGNITO_USERPOOL_ID == "us-east-1_TestPool"
    assert settings.ENVIRONMENT == "test"
