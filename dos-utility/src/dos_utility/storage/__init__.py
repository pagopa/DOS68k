from .env import StorageProvider, StorageSettings, get_storage_settings
from .interface import StorageInterface, ObjectInfo
from .aws import get_aws_s3_storage
from .minio import get_minio_storage


__all__ = ["StorageInterface", "get_storage", "ObjectInfo"]



def get_storage() -> StorageInterface:
    """Get the appropriate storage interface based on configuration.
    It can also be used as a dependency in FastAPI via injection.

    Returns:
        StorageInterface: The storage interface instance.
    """
    storage_settings: StorageSettings = get_storage_settings()

    if storage_settings.STORAGE_PROVIDER is StorageProvider.AWS_S3:
        return get_aws_s3_storage()
    elif storage_settings.STORAGE_PROVIDER is StorageProvider.MINIO:
        return get_minio_storage()
