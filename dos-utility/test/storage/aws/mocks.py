from io import BytesIO
from typing import Self, Dict
from pydantic import SecretStr


class AWSClientMock:
    def list_buckets(self: Self, *args, **kwargs) -> Dict:
        return {"Buckets": []}

    def get_object(self: Self, Bucket: str, Key: str) -> Dict:
        return {"Body": BytesIO(b"mocked data")}

    def put_object(self: Self, Bucket: str, Key: str, Body: BytesIO, ContentType: str) -> None:
        pass

    def delete_object(self: Self, Bucket: str, Key: str) -> None:
        pass

    def list_objects_v2(self: Self, Bucket: str) -> Dict:
        return {"Contents": [{"Key": "mocked-object-1"}, {"Key": "mocked-object-2"}]}

class AWSClientListBucketsExceptionMock(AWSClientMock):
    def list_buckets(self: Self, *args, **kwargs) -> Dict:
        raise Exception("Mocked list_buckets exception")

class AWSStorageSettingsMock:
    AWS_ACCESS_KEY_ID: str = "admin"
    AWS_SECRET_ACCESS_KEY: SecretStr = SecretStr("minioadmin")
    AWS_REGION: str = "us-west-1"

def get_aws_storage_settings_mock() -> AWSStorageSettingsMock:
    return AWSStorageSettingsMock()

def aws_client_mock(*args, **kwargs) -> AWSClientMock:
    return AWSClientMock()

def aws_client_list_buckets_exception_mock(*args, **kwargs) -> AWSClientListBucketsExceptionMock:
    return AWSClientListBucketsExceptionMock()