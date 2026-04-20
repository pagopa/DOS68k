from typing import BinaryIO, Self, List
from dataclasses import dataclass
from dos_utility.storage import StorageInterface, ObjectInfo
from dos_utility.storage.env import StorageProvider


class StorageMock(StorageInterface):
    def is_healthy(self: Self) -> bool:
        pass

    def get_object(self: Self, bucket: str, name: str) -> BinaryIO:
        pass

    def put_object(self: Self, bucket: str, name: str, data: BinaryIO, content_type: str) -> None:
        pass

    def delete_object(self: Self, bucket: str, name: str) -> None:
        pass

    def list_objects(self: Self, bucket: str) -> List[ObjectInfo]:
        pass

class AWSS3Mock(StorageMock):
    pass

class MinioMock(StorageMock):
    pass

def get_aws_s3_storage_mock() -> StorageInterface:
    return AWSS3Mock()

def get_minio_storage_mock() -> StorageInterface:
    return MinioMock()

@dataclass
class StorageSettingsMock:
    STORAGE_PROVIDER: str

def get_storage_settings_aws_mock():
    return StorageSettingsMock(STORAGE_PROVIDER=StorageProvider.AWS_S3)

def get_storage_settings_minio_mock():
    return StorageSettingsMock(STORAGE_PROVIDER=StorageProvider.MINIO)