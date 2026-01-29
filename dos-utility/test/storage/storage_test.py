import pytest

from dos_utility.storage import StorageInterface, get_storage
from dos_utility.storage.env import get_storage_settings

from test.storage.mocks import get_aws_s3_storage_mock, get_minio_storage_mock


@pytest.mark.parametrize(
    "provider_env, expected_getter",
    [
        ("aws_s3", get_aws_s3_storage_mock),
        ("minio", get_minio_storage_mock),
    ],
)
def test_get_storage(monkeypatch: pytest.MonkeyPatch, provider_env: str, expected_getter) -> None:
    get_storage_settings.cache_clear()

    monkeypatch.setenv("STORAGE_PROVIDER", provider_env)
    monkeypatch.setattr("dos_utility.storage.aws.get_aws_s3_storage", expected_getter)
    monkeypatch.setattr("dos_utility.storage.minio.get_minio_storage", expected_getter)

    storage: StorageInterface = get_storage()

    assert isinstance(storage, StorageInterface)