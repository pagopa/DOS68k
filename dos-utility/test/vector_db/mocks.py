from dataclasses import dataclass
from typing import Self, List, Optional
from dos_utility.vector_db.interface import VectorDBInterface, ObjectData, SemanticSearchResult
from dos_utility.vector_db.env import VectorDBProvider



@dataclass
class VectorDBSettingsMock:
    VECTOR_DB_PROVIDER: VectorDBProvider

def get_vector_db_settings_qdrant_mock():
    return VectorDBSettingsMock(VECTOR_DB_PROVIDER=VectorDBProvider.QDRANT)

def get_vector_db_settings_redis_mock():
    return VectorDBSettingsMock(VECTOR_DB_PROVIDER=VectorDBProvider.REDIS)


class VectorDBMock(VectorDBInterface):
    async def __aenter__(self: Self) -> Self:
        return self

    async def __aexit__(self: Self, exc_type, exc_value, traceback) -> None:
        pass

    async def create_index(self: Self, index_name: str, vector_dim: int) -> None:
        pass

    async def delete_index(self: Self, index_name: str) -> None:
        pass

    async def get_indexes(self: Self) -> List[str]:
        pass

    async def put_objects(self: Self, index_name: str, data: List[ObjectData], custom_keys: Optional[List[str]]=None) -> List[str]:
        pass

    async def delete_objects(self: Self, index_name: str, ids: List[str]) -> None:
        pass

    async def semantic_search(self: Self, index_name: str, embedding_query: List[float], max_results: int, score_threshold: float) -> List[SemanticSearchResult]:
        pass

class QdrantVectorDBMock(VectorDBMock):
    pass

class RedisVectorDBMock(VectorDBMock):
    pass

def get_qdrant_vector_db_mock() -> VectorDBInterface:
    return QdrantVectorDBMock()

def get_redis_vector_db_mock() -> VectorDBInterface:
    return RedisVectorDBMock()