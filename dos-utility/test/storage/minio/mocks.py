from io import BytesIO
from typing import Self, Dict, Iterator
from minio.datatypes import Object
from pydantic import SecretStr


class HTTPResponseMock:
    def __init__(self: Self, data: bytes) -> None:
        self._data: BytesIO = BytesIO(data)

    def read(self: Self) -> bytes:
        return self._data.read()

    def close(self: Self) -> None:
        pass

    def release_conn(self: Self) -> None:
        pass

class MinioMock:
    def __init__(self: Self, *args, **kwargs) -> None:
        pass

    def list_buckets(self: Self, *args, **kwargs) -> Dict:
        return {"Buckets": []}

    def get_object(self: Self, bucket_name: str, object_name: str) -> HTTPResponseMock:
        return HTTPResponseMock(b"mocked data")

    def put_object(self: Self, bucket_name: str, object_name: str, data: BytesIO, content_type: str) -> None:
        pass

    def remove_object(self: Self, bucket_name: str, object_name: str) -> None:
        pass

    def list_objects(self: Self, bucket_name: str) -> Iterator[Object]:
        return [Object(bucket_name="bucket-name", object_name="mocked-object-1"), Object(bucket_name="bucket-name", object_name="mocked-object-2")]

class MinioListBucketsExceptionMock(MinioMock):
    def list_buckets(self: Self, *args, **kwargs) -> Dict:
        raise Exception("Mocked list_buckets exception")

class MinioStorageSettingsMock:
    MINIO_ENDPOINT: str = "mock-endpoint"
    MINIO_PORT: int = 9000
    MINIO_ACCESS_KEY: str = "mock-access-key"
    MINIO_SECRET_KEY: SecretStr = SecretStr("mock-secret-key")
    MINIO_REGION: str = "mock-region"

def get_minio_storage_settings_mock() -> MinioStorageSettingsMock:
    return MinioStorageSettingsMock()
