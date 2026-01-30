import logging
import boto3

from botocore.response import StreamingBody
from typing import Self, BinaryIO, Dict, List

from ..interface import StorageInterface, ObjectInfo
from .env import AWSStorageSettings, get_aws_storage_settings


class AWSS3(StorageInterface):
    def __init__(self: Self) -> None:
        self._settings: AWSStorageSettings = get_aws_storage_settings()

        if self._settings.S3_ENDPOINT is not None:
            self.client = boto3.client(
                "s3",
                region_name=self._settings.AWS_REGION,
                endpoint_url=self._settings.S3_ENDPOINT, # Used for localstack or custom S3 endpoints
            )
        else:
            self.client = boto3.client("s3", region_name=self._settings.AWS_REGION)

    def is_healthy(self: Self) -> bool:
        # Simple health check to verify S3 connectivity
        try:
            _ = self.client.list_buckets(MaxBuckets=1)
        except Exception as e:
            logging.error(f"S3 health check failed: {e}")

            return False

        return True

    def get_object(self: Self, bucket: str, name: str) -> BinaryIO:
        response: Dict = self.client.get_object(Bucket=bucket, Key=name)
        body: StreamingBody = response["Body"]

        return body.read()

    def put_object(self: Self, bucket: str, name: str, data: BinaryIO, content_type: str) -> None:
        self.client.put_object(Bucket=bucket, Key=name, Body=data, ContentType=content_type)

    def delete_object(self: Self, bucket: str, name: str) -> None:
        self.client.delete_object(Bucket=bucket, Key=name)

    def list_objects(self: Self, bucket: str) -> List[ObjectInfo]:
        response: Dict = self.client.list_objects_v2(Bucket=bucket)
        objects: List[ObjectInfo] = []

        for obj in response.get("Contents", []):
            objects.append(ObjectInfo(key=obj["Key"]))

        return objects


def get_aws_s3_storage() -> AWSS3:
    return AWSS3()