from typing import Self, Dict, Any, List
from qdrant_client.conversions.common_types import Points
from qdrant_client.http.models import CollectionDescription, UpdateResult, UpdateStatus, CollectionsResponse, QueryResponse, ScoredPoint



class QdrantVectorDBSettingsMock:
    QDRANT_HOST: str = "http://localhost:6333"
    QDRANT_PORT: str = "test_collection"

def get_qdrant_vector_db_settings_mock() -> QdrantVectorDBSettingsMock:
    return QdrantVectorDBSettingsMock()

class AsyncQdrantClientMock:
    def __init__(self: Self, *args, **kwargs) -> None:
        pass

    async def close(self: Self) -> None:
        pass

    async def collection_exists(self: Self, collection_name: str) -> bool:
        return False

    async def create_collection(self: Self, collection_name: str, vectors_config: Dict[str, Any]) -> bool:
        return True

    async def delete_collection(self: Self, collection_name: str) -> bool:
        return True

    async def get_collections(self: Self) -> CollectionsResponse:
        return CollectionsResponse(collections=[
            CollectionDescription(name="test_collection"),
            CollectionDescription(name="another_collection"),
        ])

    async def upsert(self: Self, collection_name: str, points: Points, wait: bool) -> UpdateResult:
        return UpdateResult(status=UpdateStatus.COMPLETED)

    async def delete(self: Self, collection_name: str, points_selector: List[str], wait: bool) -> UpdateResult:
        return UpdateResult(status=UpdateStatus.COMPLETED)

    async def query_points(self: Self, collection_name: str, query: List[float], limit: int, using: str) -> QueryResponse:
        return QueryResponse(points=[
            ScoredPoint(
                id="obj1",
                version=1,
                score=0.95,
                payload={
                    "filename": "file1.txt",
                    "chunk_id": 0,
                    "content": "This is the content of file 1.",
                },
            ),
            ScoredPoint(
                id="obj2",
                version=1,
                score=0.85,
                payload={
                    "filename": "file2.txt",
                    "chunk_id": 0,
                    "content": "This is the content of file 2.",
                },
            ),
            ScoredPoint(
                id="obj3",
                version=1,
                score=0.35,
                payload={
                    "filename": "file3.txt",
                    "chunk_id": 0,
                    "content": "This is the content of file 3.",
                },
            ),
        ])

class AsyncQdrantClientCollectionAlreadyExistsMock(AsyncQdrantClientMock):
    async def collection_exists(self: Self, collection_name: str) -> bool:
        return True

class AsyncQdrantClientCreateCollectionFailedMock(AsyncQdrantClientMock):
    async def create_collection(self: Self, collection_name: str, vectors_config: Dict[str, Any]) -> bool:
        return False

class AsyncQdrantClientDeleteCollectionFailedMock(AsyncQdrantClientMock):
    async def delete_collection(self: Self, collection_name: str) -> bool:
        return False

class AsyncQdrantClientPutObjectsFailedMock(AsyncQdrantClientMock):
    async def upsert(self: Self, collection_name: str, points: Points, wait: bool) -> UpdateResult:
        return UpdateResult(status=UpdateStatus.ACKNOWLEDGED)

class AsyncQdrantClientDeleteObjectsFailedMock(AsyncQdrantClientMock):
    async def delete(self: Self, collection_name: str, points_selector: List[str], wait: bool) -> UpdateResult:
        return UpdateResult(status=UpdateStatus.ACKNOWLEDGED)