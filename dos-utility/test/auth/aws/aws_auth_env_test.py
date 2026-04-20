import pytest
from pydantic import ValidationError

from dos_utility.auth.aws.env import AWSAuthSettings


_REQUIRED_ENV = {
    "AWS_REGION": "us-east-1",
    "AWS_ENDPOINT_URL": "http://localhost:4566",
    "AWS_ACCESS_KEY_ID": "test-key",
    "AWS_SECRET_ACCESS_KEY": "test-secret",
    "AWS_COGNITO_USERPOOL_ID": "us-east-1_TestPool",
}


def test_aws_auth_settings_valid(monkeypatch: pytest.MonkeyPatch):
    for key, value in _REQUIRED_ENV.items():
        monkeypatch.setenv(key, value)

    settings = AWSAuthSettings()

    assert settings.AWS_REGION == "us-east-1"
    assert settings.AWS_COGNITO_USERPOOL_ID == "us-east-1_TestPool"
    assert settings.AWS_SECRET_ACCESS_KEY.get_secret_value() == "test-secret"


def test_aws_auth_settings_default_environment(monkeypatch: pytest.MonkeyPatch):
    for key, value in _REQUIRED_ENV.items():
        monkeypatch.setenv(key, value)

    settings = AWSAuthSettings()

    assert settings.ENVIRONMENT == "dev"


def test_aws_auth_settings_custom_environment(monkeypatch: pytest.MonkeyPatch):
    for key, value in _REQUIRED_ENV.items():
        monkeypatch.setenv(key, value)
    monkeypatch.setenv("ENVIRONMENT", "test")

    settings = AWSAuthSettings()

    assert settings.ENVIRONMENT == "test"


def test_aws_auth_settings_missing_region_raises(monkeypatch: pytest.MonkeyPatch):
    for key, value in _REQUIRED_ENV.items():
        monkeypatch.setenv(key, value)
    monkeypatch.delenv("AWS_REGION")

    with pytest.raises(ValidationError):
        AWSAuthSettings()


def test_get_aws_auth_settings(monkeypatch: pytest.MonkeyPatch):
    from dos_utility.auth.aws.env import get_aws_auth_settings
    get_aws_auth_settings.cache_clear()

    for key, value in _REQUIRED_ENV.items():
        monkeypatch.setenv(key, value)

    settings = get_aws_auth_settings()

    assert settings.AWS_REGION == "us-east-1"
    assert settings.AWS_COGNITO_USERPOOL_ID == "us-east-1_TestPool"
