from dos_utility.storage import StorageInterface


class AWSS3Mock(StorageInterface):
    pass

class MinioMock(StorageInterface):
    pass

def get_aws_s3_storage_mock() -> StorageInterface:
    return AWSS3Mock()

def get_minio_storage_mock() -> StorageInterface:
    return MinioMock()