from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import Self, BinaryIO, List


@dataclass
class ObjectInfo:
    """
    Information about an object stored in the storage service.

    Attributes:
        key (str): The key (name) of the object. It can be use to retrieve the object with the `get_object` method.
    """
    key: str


class StorageInterface(ABC):
    @abstractmethod
    def is_healthy(self: Self) -> bool:
        """Check if the storage service is healthy and reachable.
        If any exception occurs during the check, it should be interpreted as unhealthy and return False.

        Returns:
            bool: True if the storage service is healthy, False otherwise.
        """
        ...

    @abstractmethod
    def get_object(self: Self, bucket: str, name: str) -> BinaryIO:
        """Retrieve an object from the storage.

        Args:
            bucket (str): The name of the bucket.
            name (str): The name of the object.

        Returns:
            BinaryIO: The binary data of the object.
        """
        ...

    @abstractmethod
    def put_object(self: Self, bucket: str, name: str, data: BinaryIO, content_type: str) -> None:
        """Store an object in the storage.

        Args:
            bucket (str): The name of the bucket.
            name (str): The name of the object.
            data (BinaryIO): The binary data of the object.
            content_type (str): The content type of the object.
        """
        ...

    @abstractmethod
    def delete_object(self: Self, bucket: str, name: str) -> None:
        """Delete an object from the storage.

        Args:
            bucket (str): The name of the bucket.
            name (str): The name of the object.
        """
        ...

    @abstractmethod
    def list_objects(self: Self, bucket: str) -> List[ObjectInfo]:
        """List all objects in a bucket.

        Args:
            bucket (str): The name of the bucket.

        Returns:
            List[ObjectInfo]: A list of ObjectInfo representing the objects in the bucket.
        """
        ...