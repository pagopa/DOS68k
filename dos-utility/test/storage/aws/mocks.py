from dataclasses import dataclass
from io import BytesIO
from typing import Self, Dict, Optional


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

@dataclass
class AWSStorageSettingsMock:
    S3_ENDPOINT: Optional[str]
    S3_REGION: str

def get_aws_storage_settings_mock() -> AWSStorageSettingsMock:
    return AWSStorageSettingsMock(
        S3_ENDPOINT=None,
        S3_REGION="us-east-1"
    )

def get_aws_storage_settings_with_endpoint_mock() -> AWSStorageSettingsMock:
    return AWSStorageSettingsMock(
        S3_ENDPOINT="http://localhost:4566",
        S3_REGION="us-east-1"
    )

def aws_client_mock(*args, **kwargs) -> AWSClientMock:
    return AWSClientMock()

def aws_client_list_buckets_exception_mock(*args, **kwargs) -> AWSClientListBucketsExceptionMock:
    return AWSClientListBucketsExceptionMock()