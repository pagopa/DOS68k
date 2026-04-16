import pytest

from dos_utility import storage
from dos_utility.storage import StorageInterface, get_storage
from dos_utility.storage.env import get_storage_settings

from test.storage.mocks import get_aws_s3_storage_mock, get_minio_storage_mock, get_storage_settings_aws_mock, get_storage_settings_minio_mock


def test_get_storage_aws(monkeypatch: pytest.MonkeyPatch) -> None:
    get_storage_settings.cache_clear()

    monkeypatch.setattr(storage, "get_storage_settings", get_storage_settings_aws_mock)
    monkeypatch.setattr(storage, "get_aws_s3_storage", get_aws_s3_storage_mock)

    storage_interface: StorageInterface = get_storage()

    assert isinstance(storage_interface, StorageInterface)

def test_get_storage_minio(monkeypatch: pytest.MonkeyPatch) -> None:
    get_storage_settings.cache_clear()

    monkeypatch.setattr(storage, "get_storage_settings", get_storage_settings_minio_mock)
    monkeypatch.setattr(storage, "get_minio_storage", get_minio_storage_mock)

    storage_interface: StorageInterface = get_storage()

    assert isinstance(storage_interface, StorageInterface)
