import pytest

from dos_utility.storage.env import StorageProvider, StorageSettings, get_storage_settings


@pytest.mark.parametrize(
    "env_value, expected_provider",
    [
        ("aws_s3", StorageProvider.AWS_S3),
        ("minio", StorageProvider.MINIO),
    ],
)
def test_get_storage_settings(monkeypatch: pytest.MonkeyPatch, env_value: str, expected_provider: StorageProvider) -> None:
    get_storage_settings.cache_clear()

    monkeypatch.setenv("STORAGE_PROVIDER", env_value)

    settings: StorageSettings = get_storage_settings()

    assert settings.STORAGE_PROVIDER is expected_provider
