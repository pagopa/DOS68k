import logging

from urllib3.response import HTTPResponse
from minio import Minio
from minio.datatypes import Object
from typing import Self, BinaryIO, List, Iterator

from ..interface import StorageInterface, ObjectInfo
from .env import MinIOStorageSettings, get_minio_storage_settings


class MinIO(StorageInterface):
    def __init__(self: Self):
        self._settings: MinIOStorageSettings = get_minio_storage_settings()
        self.client: Minio = Minio(
            endpoint=f"{self._settings.MINIO_ENDPOINT}:{self._settings.MINIO_PORT}",
            access_key=self._settings.MINIO_ACCESS_KEY,
            secret_key=self._settings.MINIO_SECRET_KEY.get_secret_value(),
            region=self._settings.MINIO_REGION,
        )

    def is_healthy(self: Self) -> bool:
        try:
            _ = self.client.list_buckets()
        except Exception as e:
            logging.error(f"MinIO health check failed: {e}")

            return False

        return True

    def get_object(self: Self, bucket: str, name: str) -> BinaryIO:
        try:
            response: HTTPResponse = self.client.get_object(bucket_name=bucket, object_name=name)
        finally:
            response.close()
            response.release_conn()

        return response.read()

    def put_object(self: Self, bucket: str, name: str, data: BinaryIO, content_type: str) -> None:
        self.client.put_object(bucket_name=bucket, object_name=name, data=data, content_type=content_type)

    def delete_object(self: Self, bucket: str, name: str) -> None:
        self.client.remove_object(bucket_name=bucket, object_name=name)

    def list_objects(self: Self, bucket: str) -> List[ObjectInfo]:
        response: Iterator[Object] = self.client.list_objects(bucket_name=bucket)
        objects: List[ObjectInfo] = []

        for obj in response:
            objects.append(ObjectInfo(key=obj.object_name))

        return objects


def get_minio_storage() -> MinIO:
    return MinIO()