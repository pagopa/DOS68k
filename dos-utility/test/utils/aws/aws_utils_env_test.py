import pytest

from dos_utility.utils.aws.env import AWSCredentialsSettings, get_aws_credentials_settings


def test_get_aws_credentials_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    get_aws_credentials_settings.cache_clear()

    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "test-access-key")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "test-secret-key")

    settings: AWSCredentialsSettings = get_aws_credentials_settings()

    assert settings.AWS_ACCESS_KEY_ID == "test-access-key"
    assert settings.AWS_SECRET_ACCESS_KEY.get_secret_value() == "test-secret-key"
