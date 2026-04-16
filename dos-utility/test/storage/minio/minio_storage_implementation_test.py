import pytest

from typing import BinaryIO, List
from dos_utility.storage.minio import implementation
from dos_utility.storage.minio.implementation import MinIO
from dos_utility.storage.minio.env import get_minio_storage_settings

from test.storage.minio.mocks import get_minio_storage_settings_mock, MinioMock, MinioListBucketsExceptionMock


def test_instantiate_minio(monkeypatch: pytest.MonkeyPatch):
    get_minio_storage_settings.cache_clear()

    monkeypatch.setattr(implementation, "get_minio_storage_settings", get_minio_storage_settings_mock)
    monkeypatch.setattr(implementation, "Minio", MinioMock)

    minio: MinIO = MinIO()

    assert isinstance(minio, MinIO)

def test_minio_is_healthy(monkeypatch: pytest.MonkeyPatch):
    get_minio_storage_settings.cache_clear()

    monkeypatch.setattr(implementation, "get_minio_storage_settings", get_minio_storage_settings_mock)
    monkeypatch.setattr(implementation, "Minio", MinioMock)

    minio: MinIO = MinIO()
    is_healthy: bool = minio.is_healthy()

    assert is_healthy is True

def test_minio_is_healthy_failure(monkeypatch: pytest.MonkeyPatch):
    get_minio_storage_settings.cache_clear()

    monkeypatch.setattr(implementation, "get_minio_storage_settings", get_minio_storage_settings_mock)
    monkeypatch.setattr(implementation, "Minio", MinioListBucketsExceptionMock)

    minio: MinIO = MinIO()
    is_healthy: bool = minio.is_healthy()

    assert is_healthy is False

def test_minio_get_object(monkeypatch: pytest.MonkeyPatch):
    get_minio_storage_settings.cache_clear()

    monkeypatch.setattr(implementation, "get_minio_storage_settings", get_minio_storage_settings_mock)
    monkeypatch.setattr(implementation, "Minio", MinioMock)

    minio: MinIO = MinIO()
    data: BinaryIO = minio.get_object(bucket="test-bucket", name="test-object")

    assert data is not None

def test_minio_put_object(monkeypatch: pytest.MonkeyPatch):
    get_minio_storage_settings.cache_clear()

    monkeypatch.setattr(implementation, "get_minio_storage_settings", get_minio_storage_settings_mock)
    monkeypatch.setattr(implementation, "Minio", MinioMock)

    minio: MinIO = MinIO()
    minio.put_object(bucket="test-bucket", name="test-object", data=b"test data", content_type="text/plain")

    assert True

def test_minio_delete_object(monkeypatch: pytest.MonkeyPatch):
    get_minio_storage_settings.cache_clear()

    monkeypatch.setattr(implementation, "get_minio_storage_settings", get_minio_storage_settings_mock)
    monkeypatch.setattr(implementation, "Minio", MinioMock)

    minio: MinIO = MinIO()
    minio.delete_object(bucket="test-bucket", name="test-object")

    assert True

def test_minio_list_objects(monkeypatch: pytest.MonkeyPatch):
    get_minio_storage_settings.cache_clear()

    monkeypatch.setattr(implementation, "get_minio_storage_settings", get_minio_storage_settings_mock)
    monkeypatch.setattr(implementation, "Minio", MinioMock)

    minio: MinIO = MinIO()
    objects: List = minio.list_objects(bucket="test-bucket")

    assert objects is not None

def test_get_minio_storage(monkeypatch: pytest.MonkeyPatch):
    get_minio_storage_settings.cache_clear()

    monkeypatch.setattr(implementation, "get_minio_storage_settings", get_minio_storage_settings_mock)
    monkeypatch.setattr(implementation, "Minio", MinioMock)

    minio: MinIO = implementation.get_minio_storage()

    assert isinstance(minio, MinIO)