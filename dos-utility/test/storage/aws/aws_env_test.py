import pytest

from dos_utility.storage.aws.env import AWSStorageSettings, get_aws_storage_settings


def test_get_aws_storage_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    get_aws_storage_settings.cache_clear()

    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "test-access-key")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "test-secret-key")
    monkeypatch.setenv("AWS_REGION", "test-region")

    settings: AWSStorageSettings = get_aws_storage_settings()

    assert settings.AWS_ACCESS_KEY_ID == "test-access-key"
    assert settings.AWS_SECRET_ACCESS_KEY.get_secret_value() == "test-secret-key"
    assert settings.AWS_REGION == "test-region"
