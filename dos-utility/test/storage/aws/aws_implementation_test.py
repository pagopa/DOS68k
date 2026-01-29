import pytest

from typing import BinaryIO, List
from dos_utility.storage.aws import implementation
from dos_utility.storage.aws.implementation import AWSS3

from test.storage.aws.mocks import get_aws_storage_settings_mock, aws_client_mock, aws_client_list_buckets_exception_mock


def test_instantiate_aws_s3(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(implementation, "get_aws_storage_settings", get_aws_storage_settings_mock)
    monkeypatch.setattr(implementation.boto3, "client", aws_client_mock)

    aws_s3: AWSS3 = AWSS3()

    assert isinstance(aws_s3, AWSS3)

def test_aws_s3_is_healthy(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(implementation, "get_aws_storage_settings", get_aws_storage_settings_mock)
    monkeypatch.setattr(implementation.boto3, "client", aws_client_mock)

    aws_s3: AWSS3 = AWSS3()
    is_healthy: bool = aws_s3.is_healthy()

    assert is_healthy is True

def test_aws_s3_is_healthy_failure(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(implementation, "get_aws_storage_settings", get_aws_storage_settings_mock)
    monkeypatch.setattr(implementation.boto3, "client", aws_client_list_buckets_exception_mock)

    aws_s3: AWSS3 = AWSS3()
    is_healthy: bool = aws_s3.is_healthy()

    assert is_healthy is False

def test_aws_s3_get_object(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(implementation, "get_aws_storage_settings", get_aws_storage_settings_mock)
    monkeypatch.setattr(implementation.boto3, "client", aws_client_mock)

    aws_s3: AWSS3 = AWSS3()
    data: BinaryIO = aws_s3.get_object(bucket="test-bucket", name="test-object")

    assert data is not None

def test_aws_s3_put_object(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(implementation, "get_aws_storage_settings", get_aws_storage_settings_mock)
    monkeypatch.setattr(implementation.boto3, "client", aws_client_mock)

    aws_s3: AWSS3 = AWSS3()
    aws_s3.put_object(bucket="test-bucket", name="test-object", data=b"test data", content_type="text/plain")

    assert True

def test_aws_s3_delete_object(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(implementation, "get_aws_storage_settings", get_aws_storage_settings_mock)
    monkeypatch.setattr(implementation.boto3, "client", aws_client_mock)

    aws_s3: AWSS3 = AWSS3()
    aws_s3.delete_object(bucket="test-bucket", name="test-object")

    assert True

def test_aws_s3_list_objects(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(implementation, "get_aws_storage_settings", get_aws_storage_settings_mock)
    monkeypatch.setattr(implementation.boto3, "client", aws_client_mock)

    aws_s3: AWSS3 = AWSS3()
    objects: List = aws_s3.list_objects(bucket="test-bucket")

    assert objects is not None

def test_get_aws_s3_storage(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(implementation, "get_aws_storage_settings", get_aws_storage_settings_mock)
    monkeypatch.setattr(implementation.boto3, "client", aws_client_mock)

    aws_s3: AWSS3 = implementation.get_aws_s3_storage()

    assert isinstance(aws_s3, AWSS3)