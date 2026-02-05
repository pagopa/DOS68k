from typing import Self, List
from redisvl.exceptions import RedisSearchError


class RedisClientMock:
    def __init__(self: Self, *args, **kwargs):
        pass

    async def aclose(self: Self):
        pass

    async def execute_command(self: Self, *args, **kwargs) -> List[bytes]:
        if args[0] == "FT._LIST":
            return [b"index1", b"index2"]

class AsyncSearchIndexMock:
    def __init__(self: Self, *args, **kwargs):
        pass

    @classmethod
    def from_existing(cls, *args, **kwargs) -> Self:
        return cls()

    async def create(self: Self, *args, **kwargs) -> None:
        pass

    async def delete(self: Self, drop: bool) -> bool:
        return True

    async def load(self: Self, *args, **kwargs) -> List[str]:
        return ["key1", "key2"]

    async def drop_keys(self: Self, *args, **kwargs) -> int:
        return 2

    async def search(self: Self, *args, **kwargs) -> List[dict]:
        return [
            {
                "id": "key1",
                "filename": "file1.txt",
                "chunk_id": 1,
                "content": "This is a test chunk.",
                "vector_distance": 0.123,
            },
            {
                "id": "key2",
                "filename": "file2.txt",
                "chunk_id": 2,
                "content": "This is another test chunk.",
                "vector_distance": 0.356,
            },
            {
                "id": "key3",
                "filename": "file3.txt",
                "chunk_id": 3,
                "content": "This is yet another test chunk.",
                "vector_distance": 0.789,
            },
        ]

class AsyncSearchIndexCreationIndexFailedMock(AsyncSearchIndexMock):
    def create(self: Self, *args, **kwargs) -> None:
        raise Exception("Index creation failed")

class AsyncSearchIndexDeletionIndexFailedMock(AsyncSearchIndexMock):
    async def delete(self: Self, drop: bool) -> bool:
        return False

class AsyncSearchIndexRedisSearchErrorNonExistingIndexMock(AsyncSearchIndexMock):
    async def delete(self: Self, drop: bool) -> bool:
        raise RedisSearchError("Error while deleting index: Unknown Index name")

class AsyncSearchIndexDeletionIndexFailedRedisSearchErrorMock(AsyncSearchIndexMock):
    async def delete(self: Self, drop: bool) -> bool:
        raise RedisSearchError("Different RedisSearch error")

class AsyncSearchIndexPutObjectsFailedMock(AsyncSearchIndexMock):
    async def load(self: Self, *args, **kwargs) -> List[str]:
        raise Exception("Failed to put objects")

class AsyncSearchIndexDeleteObjectsFailedMock(AsyncSearchIndexMock):
    async def drop_keys(self: Self, *args, **kwargs) -> int:
        raise Exception("Failed to delete objects")