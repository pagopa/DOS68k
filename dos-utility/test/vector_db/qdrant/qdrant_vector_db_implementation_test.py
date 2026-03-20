import pytest

from typing import List

from dos_utility.vector_db import ObjectData
from dos_utility.vector_db.qdrant import implementation
from dos_utility.vector_db.qdrant import QdrantVectorDB, get_qdrant_vector_db
from dos_utility.vector_db.qdrant.env import get_qdrant_vector_db_settings
from dos_utility.vector_db.exceptions import IndexCreationException, IndexDeletionException, PutObjectsException, DeleteObjectsException

from test.vector_db.qdrant.mocks import (
    get_qdrant_vector_db_settings_mock,
    AsyncQdrantClientMock,
    AsyncQdrantClientCollectionAlreadyExistsMock,
    AsyncQdrantClientCreateCollectionFailedMock,
    AsyncQdrantClientDeleteCollectionFailedMock,
    AsyncQdrantClientPutObjectsFailedMock,
    AsyncQdrantClientDeleteObjectsFailedMock,
)


def test_instantiate_qdrant_vector_db(monkeypatch: pytest.MonkeyPatch):
    get_qdrant_vector_db_settings.cache_clear()

    monkeypatch.setattr(implementation, "get_qdrant_vector_db_settings", get_qdrant_vector_db_settings_mock)

    qdrant_db: QdrantVectorDB = QdrantVectorDB()

    assert isinstance(qdrant_db, QdrantVectorDB)

@pytest.mark.asyncio
async def test_qdrant_aenter_aexit(monkeypatch: pytest.MonkeyPatch):
    get_qdrant_vector_db_settings.cache_clear()

    monkeypatch.setattr(implementation, "get_qdrant_vector_db_settings", get_qdrant_vector_db_settings_mock)
    monkeypatch.setattr(implementation, "AsyncQdrantClient", AsyncQdrantClientMock)

    async with QdrantVectorDB() as db:
        assert isinstance(db, QdrantVectorDB)

@pytest.mark.asyncio
async def test_create_index_already_exists(monkeypatch: pytest.MonkeyPatch):
    get_qdrant_vector_db_settings.cache_clear()

    monkeypatch.setattr(implementation, "get_qdrant_vector_db_settings", get_qdrant_vector_db_settings_mock)
    monkeypatch.setattr(implementation, "AsyncQdrantClient", AsyncQdrantClientCollectionAlreadyExistsMock)

    async with QdrantVectorDB() as db:
        await db.create_index(index_name="test_index", vector_dim=128)

    assert True

@pytest.mark.asyncio
async def test_create_index_failed(monkeypatch: pytest.MonkeyPatch):
    get_qdrant_vector_db_settings.cache_clear()

    monkeypatch.setattr(implementation, "get_qdrant_vector_db_settings", get_qdrant_vector_db_settings_mock)
    monkeypatch.setattr(implementation, "AsyncQdrantClient", AsyncQdrantClientCreateCollectionFailedMock)

    index_name: str = "test_index"

    async with QdrantVectorDB() as db:
        with pytest.raises(expected_exception=IndexCreationException, match=f"Qdrant gave a negative output when creating index '{index_name}'"):
            await db.create_index(index_name=index_name, vector_dim=128)

@pytest.mark.asyncio
async def test_create_index_success(monkeypatch: pytest.MonkeyPatch):
    get_qdrant_vector_db_settings.cache_clear()

    monkeypatch.setattr(implementation, "get_qdrant_vector_db_settings", get_qdrant_vector_db_settings_mock)
    monkeypatch.setattr(implementation, "AsyncQdrantClient", AsyncQdrantClientMock)

    async with QdrantVectorDB() as db:
        await db.create_index(index_name="test_index", vector_dim=128)

    assert True

@pytest.mark.asyncio
async def test_delete_index_failed(monkeypatch: pytest.MonkeyPatch):
    get_qdrant_vector_db_settings.cache_clear()

    monkeypatch.setattr(implementation, "get_qdrant_vector_db_settings", get_qdrant_vector_db_settings_mock)
    monkeypatch.setattr(implementation, "AsyncQdrantClient", AsyncQdrantClientDeleteCollectionFailedMock)

    index_name: str = "test_index"

    async with QdrantVectorDB() as db:
        with pytest.raises(expected_exception=IndexDeletionException, match=f"Qdrant gave a negative output when deleting index '{index_name}'"):
            await db.delete_index(index_name=index_name)

@pytest.mark.asyncio
async def test_delete_index_success(monkeypatch: pytest.MonkeyPatch):
    get_qdrant_vector_db_settings.cache_clear()

    monkeypatch.setattr(implementation, "get_qdrant_vector_db_settings", get_qdrant_vector_db_settings_mock)
    monkeypatch.setattr(implementation, "AsyncQdrantClient", AsyncQdrantClientMock)

    async with QdrantVectorDB() as db:
        await db.delete_index(index_name="test_index")

    assert True

@pytest.mark.asyncio
async def test_get_indexes(monkeypatch: pytest.MonkeyPatch):
    get_qdrant_vector_db_settings.cache_clear()

    monkeypatch.setattr(implementation, "get_qdrant_vector_db_settings", get_qdrant_vector_db_settings_mock)
    monkeypatch.setattr(implementation, "AsyncQdrantClient", AsyncQdrantClientMock)

    async with QdrantVectorDB() as db:
        indexes: List[str] = await db.get_indexes()

    assert isinstance(indexes, list)

@pytest.mark.asyncio
async def test_put_objects_with_custom_keys(monkeypatch: pytest.MonkeyPatch):
    get_qdrant_vector_db_settings.cache_clear()

    monkeypatch.setattr(implementation, "get_qdrant_vector_db_settings", get_qdrant_vector_db_settings_mock)
    monkeypatch.setattr(implementation, "AsyncQdrantClient", AsyncQdrantClientMock)

    async with QdrantVectorDB() as db:
        ids: List[str] = await db.put_objects(
            index_name="test_index",
            data=[
                ObjectData(
                    filename="file1.txt",
                    chunk_id=0,
                    content="This is the content of file 1.",
                    embedding=[0.1] * 128,
                ),
            ],
            custom_keys=["key1", "key2"],
        )

    assert isinstance(ids, list)

@pytest.mark.asyncio
async def test_put_objects_without_custom_keys(monkeypatch: pytest.MonkeyPatch):
    get_qdrant_vector_db_settings.cache_clear()

    monkeypatch.setattr(implementation, "get_qdrant_vector_db_settings", get_qdrant_vector_db_settings_mock)
    monkeypatch.setattr(implementation, "AsyncQdrantClient", AsyncQdrantClientMock)

    async with QdrantVectorDB() as db:
        ids: List[str] = await db.put_objects(
            index_name="test_index",
            data=[
                ObjectData(
                    filename="file1.txt",
                    chunk_id=0,
                    content="This is the content of file 1.",
                    embedding=[0.1] * 128,
                ),
            ],
        )

    assert isinstance(ids, list)

@pytest.mark.asyncio
async def test_put_objects_upsert_failed(monkeypatch: pytest.MonkeyPatch):
    get_qdrant_vector_db_settings.cache_clear()

    monkeypatch.setattr(implementation, "get_qdrant_vector_db_settings", get_qdrant_vector_db_settings_mock)
    monkeypatch.setattr(implementation, "AsyncQdrantClient", AsyncQdrantClientPutObjectsFailedMock)

    index_name: str = "test_index"

    async with QdrantVectorDB() as db:
        with pytest.raises(expected_exception=PutObjectsException, match=f"Adding objects to index '{index_name}' did not complete successfully."):
            await db.put_objects(
                index_name=index_name,
                data=[
                    ObjectData(
                        filename="file1.txt",
                        chunk_id=0,
                        content="This is the content of file 1.",
                        embedding=[0.1] * 128,
                    ),
                ],
            )

@pytest.mark.asyncio
async def test_delete_objects_success(monkeypatch: pytest.MonkeyPatch):
    get_qdrant_vector_db_settings.cache_clear()

    monkeypatch.setattr(implementation, "get_qdrant_vector_db_settings", get_qdrant_vector_db_settings_mock)
    monkeypatch.setattr(implementation, "AsyncQdrantClient", AsyncQdrantClientMock)

    async with QdrantVectorDB() as db:
        await db.delete_objects(index_name="test_index", ids=["key1", "key2"])

    assert True

@pytest.mark.asyncio
async def test_delete_objects_failed(monkeypatch: pytest.MonkeyPatch):
    get_qdrant_vector_db_settings.cache_clear()

    monkeypatch.setattr(implementation, "get_qdrant_vector_db_settings", get_qdrant_vector_db_settings_mock)
    monkeypatch.setattr(implementation, "AsyncQdrantClient", AsyncQdrantClientDeleteObjectsFailedMock)

    index_name: str = "test_index"

    async with QdrantVectorDB() as db:
        with pytest.raises(expected_exception=DeleteObjectsException, match=f"Deleting objects from index '{index_name}' did not complete successfully."):
            await db.delete_objects(index_name=index_name, ids=["key1", "key2"])

@pytest.mark.asyncio
async def test_semantic_search(monkeypatch: pytest.MonkeyPatch):
    get_qdrant_vector_db_settings.cache_clear()

    monkeypatch.setattr(implementation, "get_qdrant_vector_db_settings", get_qdrant_vector_db_settings_mock)
    monkeypatch.setattr(implementation, "AsyncQdrantClient", AsyncQdrantClientMock)

    max_results: int = 5
    score_threshold: float = 0.6

    async with QdrantVectorDB() as db:
        results = await db.semantic_search(
            index_name="test_index",
            embedding_query=[0.1] * 128,
            max_results=max_results,
            score_threshold=score_threshold,
        )

    assert isinstance(results, list)
    assert len(results) <= max_results
    assert all(result.score >= score_threshold and result.score <= 1.0 for result in results)

def test_get_qdrant_vector_db(monkeypatch: pytest.MonkeyPatch):
    get_qdrant_vector_db_settings.cache_clear()

    monkeypatch.setattr(implementation, "get_qdrant_vector_db_settings", get_qdrant_vector_db_settings_mock)

    qdrant_db: QdrantVectorDB = get_qdrant_vector_db()

    assert isinstance(qdrant_db, QdrantVectorDB)
