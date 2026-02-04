import pytest

from dos_utility.storage.minio.env import MinIOStorageSettings, get_minio_storage_settings


def test_get_minio_storage_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    get_minio_storage_settings.cache_clear()

    monkeypatch.setenv("MINIO_ENDPOINT", "test-endpoint")
    monkeypatch.setenv("MINIO_PORT", "9000")
    monkeypatch.setenv("MINIO_ACCESS_KEY", "test-access-key")
    monkeypatch.setenv("MINIO_SECRET_KEY", "test-secret-key")
    monkeypatch.setenv("MINIO_REGION", "test-region")

    settings: MinIOStorageSettings = get_minio_storage_settings()

    assert settings.MINIO_ENDPOINT == "test-endpoint"
    assert settings.MINIO_PORT == 9000
    assert settings.MINIO_ACCESS_KEY == "test-access-key"
    assert settings.MINIO_SECRET_KEY.get_secret_value() == "test-secret-key"
    assert settings.MINIO_REGION == "test-region"