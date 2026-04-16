import pytest

from dos_utility.storage.aws.env import AWSStorageSettings, get_aws_storage_settings


def test_get_aws_storage_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    get_aws_storage_settings.cache_clear()

    monkeypatch.setenv("S3_ENDPOINT", "http://localhost:9000")
    monkeypatch.setenv("S3_REGION", "test-region")

    settings: AWSStorageSettings = get_aws_storage_settings()

    assert settings.S3_ENDPOINT == "http://localhost:9000"
    assert settings.S3_REGION == "test-region"
