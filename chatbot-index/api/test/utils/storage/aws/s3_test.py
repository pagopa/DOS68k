import pytest

from src.utils.storage.aws import s3

from test.mocks import AWSClientMock, AWSStorageSettingsMock

def test_s3_health_check_with_endpoint(monkeypatch: pytest.MonkeyPatch):
    aws_storage_settings_mock: AWSStorageSettingsMock = AWSStorageSettingsMock()

    monkeypatch.setattr(s3, "AWSClient", AWSClientMock)
    monkeypatch.setattr(s3, "aws_storage_settings", aws_storage_settings_mock)

    s3_client: s3.AWSS3 = s3.AWSS3()
    assert s3_client.health_check() is None

def test_s3_health_check_without_endpoint(monkeypatch: pytest.MonkeyPatch):
    aws_storage_settings_mock: AWSStorageSettingsMock = AWSStorageSettingsMock()
    aws_storage_settings_mock.s3_endpoint = None

    monkeypatch.setattr(s3, "AWSClient", AWSClientMock)
    monkeypatch.setattr(s3, "aws_storage_settings", aws_storage_settings_mock)

    s3_client: s3.AWSS3 = s3.AWSS3()
    assert s3_client.health_check() is None
