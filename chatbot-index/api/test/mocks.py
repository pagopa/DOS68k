from typing import Self, List, Optional

from dos_utility.vector_db import VectorDBInterface, ObjectData, SemanticSearchResult


class QueueMock:
    # Mock Redis client for testing
    def __init__(self: Self):
        self.healthy: bool = True

    async def is_healthy(self: Self) -> bool:
        return self.healthy


class StorageMock:
    def __init__(self: Self):
        self.healthy: bool = True

    def is_healthy(self: Self) -> bool:
        return self.healthy


class VectorDBMock(VectorDBInterface):
    def __init__(self: Self, indexes: Optional[List[str]] = None):
        self._indexes: List[str] = indexes if indexes is not None else []

    async def __aenter__(self: Self) -> Self:
        return self

    async def __aexit__(self: Self, exc_type, exc_value, traceback) -> None:
        pass

    async def is_healthy(self: Self) -> bool:
        return True

    async def create_index(self: Self, index_name: str, vector_dim: int) -> None:
        self._indexes.append(index_name)

    async def delete_index(self: Self, index_name: str) -> None:
        self._indexes.remove(index_name)

    async def get_indexes(self: Self) -> List[str]:
        return list(self._indexes)

    async def put_objects(
        self: Self,
        index_name: str,
        data: List[ObjectData],
        custom_keys: Optional[List[str]] = None,
    ) -> List[str]:
        return [str(i) for i in range(len(data))]

    async def delete_objects(self: Self, index_name: str, ids: List[str]) -> None:
        pass

    async def search(
        self: Self,
        index_name: str,
        query_embedding: List[float],
        top_k: int = 5,
        score_threshold: float = 0.0,
    ) -> List[SemanticSearchResult]:
        return []

    async def semantic_search(
        self: Self,
        index_name: str,
        query_embedding: List[float],
        top_k: int = 5,
        score_threshold: float = 0.0,
    ) -> List[SemanticSearchResult]:
        return []
