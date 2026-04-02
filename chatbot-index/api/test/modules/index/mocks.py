from typing import Self, List
from fastapi import HTTPException, status

from dos_utility.vector_db import VectorDBInterface, IndexCreationException, IndexDeletionException


# ---------------------------------------------------------------------------
# Shared data fixtures
# ---------------------------------------------------------------------------

MOCK_USER_ID = "550e8400-e29b-41d4-a716-446655440000"
MOCK_INDEX_ID = "test-index"
MOCK_EXISTING_INDEXES = ["index-1", "index-2"]


# ---------------------------------------------------------------------------
# VectorDB mocks (for service tests)
# ---------------------------------------------------------------------------

class MockVectorDBWithIndexes:
    """Mock VectorDB that contains some pre-existing indexes."""

    def __init__(self: Self):
        self._indexes: List[str] = list(MOCK_EXISTING_INDEXES)

    async def get_indexes(self: Self) -> List[str]:
        return list(self._indexes)

    async def create_index(self: Self, index_name: str, vector_dim: int) -> None:
        self._indexes.append(index_name)

    async def delete_index(self: Self, index_name: str) -> None:
        self._indexes.remove(index_name)


class MockVectorDBEmpty:
    """Mock VectorDB with no indexes."""

    async def get_indexes(self: Self) -> List[str]:
        return []

    async def create_index(self: Self, index_name: str, vector_dim: int) -> None:
        pass

    async def delete_index(self: Self, index_name: str) -> None:
        pass


class MockVectorDBCreateFails:
    """Mock VectorDB where create_index always raises IndexCreationException."""

    async def get_indexes(self: Self) -> List[str]:
        return []

    async def create_index(self: Self, index_name: str, vector_dim: int) -> None:
        raise IndexCreationException(msg="creation failed")

    async def delete_index(self: Self, index_name: str) -> None:
        pass


class MockVectorDBDeleteFails:
    """Mock VectorDB where delete_index always raises IndexDeletionException."""

    def __init__(self: Self):
        self._indexes: List[str] = list(MOCK_EXISTING_INDEXES)

    async def get_indexes(self: Self) -> List[str]:
        return list(self._indexes)

    async def create_index(self: Self, index_name: str, vector_dim: int) -> None:
        pass

    async def delete_index(self: Self, index_name: str) -> None:
        raise IndexDeletionException(msg="deletion failed")


# ---------------------------------------------------------------------------
# Service mocks (for controller tests)
# ---------------------------------------------------------------------------

def get_index_service_create_201_mock():
    class IndexServiceMock:
        async def create_index(self, index_id: str, user_id: str):
            return {
                "index_id": index_id,
                "user_id": user_id,
                "created_at": "2024-01-01 00:00:00",
            }

    return IndexServiceMock()


def get_index_service_create_409_mock():
    class IndexServiceMock:
        async def create_index(self, index_id: str, user_id: str):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Index '{index_id}' already exists")

    return IndexServiceMock()


def get_index_service_delete_204_mock():
    class IndexServiceMock:
        async def delete_index(self, index_id: str):
            return

    return IndexServiceMock()


def get_index_service_delete_404_mock():
    class IndexServiceMock:
        async def delete_index(self, index_id: str):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Index '{index_id}' not found")

    return IndexServiceMock()


def get_index_service_get_indexes_mock():
    class IndexServiceMock:
        async def get_indexes(self):
            return ["index-1", "index-2"]

    return IndexServiceMock()


def get_index_service_get_indexes_empty_mock():
    class IndexServiceMock:
        async def get_indexes(self):
            return []

    return IndexServiceMock()
