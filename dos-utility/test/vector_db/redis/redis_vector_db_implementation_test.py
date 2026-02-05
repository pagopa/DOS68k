import pytest

from typing import List
from dos_utility.vector_db import ObjectData
from dos_utility.vector_db.redis import implementation, get_redis_vector_db
from dos_utility.vector_db.exceptions import IndexCreationException, IndexDeletionException, PutObjectsException, DeleteObjectsException
from dos_utility.vector_db.redis.implementation import RedisVectorDB

from test.utils.redis.mocks import get_queue_pool_mock
from test.vector_db.redis.mocks import (
    RedisClientMock,
    AsyncSearchIndexMock,
    AsyncSearchIndexCreationIndexFailedMock,
    AsyncSearchIndexDeletionIndexFailedMock,
    AsyncSearchIndexPutObjectsFailedMock,
    AsyncSearchIndexDeleteObjectsFailedMock,
    AsyncSearchIndexRedisSearchErrorNonExistingIndexMock,
    AsyncSearchIndexDeletionIndexFailedRedisSearchErrorMock,
)


def test_instantiate_redis_vector_db(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(implementation, "get_redis_connection_pool", get_queue_pool_mock)

    redis_vector_db: RedisVectorDB = RedisVectorDB()

    assert isinstance(redis_vector_db, RedisVectorDB)

@pytest.mark.asyncio
async def test_redis_vector_db_aenter_aexit(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(implementation, "get_redis_connection_pool", get_queue_pool_mock)
    monkeypatch.setattr(implementation, "Redis", RedisClientMock)

    async with RedisVectorDB() as db:
        assert isinstance(db, RedisVectorDB)

@pytest.mark.asyncio
async def test_redis_vector_db_create_index_success(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(implementation, "get_redis_connection_pool", get_queue_pool_mock)
    monkeypatch.setattr(implementation, "Redis", RedisClientMock)
    monkeypatch.setattr(implementation, "AsyncSearchIndex", AsyncSearchIndexMock)

    async with RedisVectorDB() as db:
        await db.create_index(index_name="test_index", vector_dim=128)

@pytest.mark.asyncio
async def test_redis_vector_db_create_index_failure(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(implementation, "get_redis_connection_pool", get_queue_pool_mock)
    monkeypatch.setattr(implementation, "Redis", RedisClientMock)
    monkeypatch.setattr(implementation, "AsyncSearchIndex", AsyncSearchIndexMock)
    monkeypatch.setattr(implementation, "AsyncSearchIndex", AsyncSearchIndexCreationIndexFailedMock)

    async with RedisVectorDB() as db:
        with pytest.raises(expected_exception=IndexCreationException, match="Index creation failed"):
            await db.create_index(index_name="test_index", vector_dim=128)

@pytest.mark.asyncio
async def test_redis_vector_db_delete_index_success(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(implementation, "get_redis_connection_pool", get_queue_pool_mock)
    monkeypatch.setattr(implementation, "Redis", RedisClientMock)
    monkeypatch.setattr(implementation, "AsyncSearchIndex", AsyncSearchIndexMock)

    async with RedisVectorDB() as db:
        await db.delete_index(index_name="test_index")

@pytest.mark.asyncio
async def test_redis_vector_db_delete_index_failure(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(implementation, "get_redis_connection_pool", get_queue_pool_mock)
    monkeypatch.setattr(implementation, "Redis", RedisClientMock)
    monkeypatch.setattr(implementation, "AsyncSearchIndex", AsyncSearchIndexDeletionIndexFailedMock)

    index_name: str = "test_index"

    async with RedisVectorDB() as db:
        with pytest.raises(expected_exception=IndexDeletionException, match=f"Failed to delete index '{index_name}'"):
            await db.delete_index(index_name="test_index")

@pytest.mark.asyncio
async def test_redis_vector_db_delete_index_redissearcherror_non_existing_index(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(implementation, "get_redis_connection_pool", get_queue_pool_mock)
    monkeypatch.setattr(implementation, "Redis", RedisClientMock)
    monkeypatch.setattr(implementation, "AsyncSearchIndex", AsyncSearchIndexRedisSearchErrorNonExistingIndexMock)

    async with RedisVectorDB() as db:
        await db.delete_index(index_name="test_index")

@pytest.mark.asyncio
async def test_redis_vector_db_delete_index_redissearcherror_generic_failure(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(implementation, "get_redis_connection_pool", get_queue_pool_mock)
    monkeypatch.setattr(implementation, "Redis", RedisClientMock)
    monkeypatch.setattr(implementation, "AsyncSearchIndex", AsyncSearchIndexDeletionIndexFailedRedisSearchErrorMock)

    index_name: str = "test_index"

    async with RedisVectorDB() as db:
        with pytest.raises(expected_exception=IndexDeletionException, match="Different RedisSearch error"):
            await db.delete_index(index_name="test_index")

@pytest.mark.asyncio
async def test_redis_vector_db_get_indexes(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(implementation, "get_redis_connection_pool", get_queue_pool_mock)
    monkeypatch.setattr(implementation, "Redis", RedisClientMock)

    async with RedisVectorDB() as db:
        indexes: List[str] = await db.get_indexes()

        assert isinstance(indexes, list)

@pytest.mark.asyncio
async def test_redis_vector_db_put_objects_with_custom_keys(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(implementation, "get_redis_connection_pool", get_queue_pool_mock)
    monkeypatch.setattr(implementation, "Redis", RedisClientMock)
    monkeypatch.setattr(implementation, "AsyncSearchIndex", AsyncSearchIndexMock)

    async with RedisVectorDB() as db:
        keys: List[str] = await db.put_objects(
            index_name="test_index",
            data=[
                ObjectData(
                    filename="file1.txt",
                    chunk_id=1,
                    content="This is a test chunk.",
                    embedding=[0.1] * 128,
                ),
                ObjectData(
                    filename="file2.txt",
                    chunk_id=2,
                    content="This is another test chunk.",
                    embedding=[0.2] * 128,
                ),
            ],
            custom_keys=["custom_key1", "custom_key2"],
        )

        assert isinstance(keys, list)

@pytest.mark.asyncio
async def test_redis_vector_db_put_objects_without_custom_keys(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(implementation, "get_redis_connection_pool", get_queue_pool_mock)
    monkeypatch.setattr(implementation, "Redis", RedisClientMock)
    monkeypatch.setattr(implementation, "AsyncSearchIndex", AsyncSearchIndexMock)

    async with RedisVectorDB() as db:
        keys: List[str] = await db.put_objects(
            index_name="test_index",
            data=[
                ObjectData(
                    filename="file1.txt",
                    chunk_id=1,
                    content="This is a test chunk.",
                    embedding=[0.1] * 128,
                ),
                ObjectData(
                    filename="file2.txt",
                    chunk_id=2,
                    content="This is another test chunk.",
                    embedding=[0.2] * 128,
                ),
            ],
        )

        assert isinstance(keys, list)

@pytest.mark.asyncio
async def test_redis_vector_db_put_objects_failure(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(implementation, "get_redis_connection_pool", get_queue_pool_mock)
    monkeypatch.setattr(implementation, "Redis", RedisClientMock)
    monkeypatch.setattr(implementation, "AsyncSearchIndex", AsyncSearchIndexPutObjectsFailedMock)

    async with RedisVectorDB() as db:
        with pytest.raises(expected_exception=PutObjectsException, match="Failed to put objects"):
            await db.put_objects(
                index_name="test_index",
                data=[
                    ObjectData(
                        filename="file1.txt",
                        chunk_id=1,
                        content="This is a test chunk.",
                        embedding=[0.1] * 128,
                    ),
                    ObjectData(
                        filename="file2.txt",
                        chunk_id=2,
                        content="This is another test chunk.",
                        embedding=[0.2] * 128,
                    ),
                ],
            )

@pytest.mark.asyncio
async def test_redis_vector_db_delete_objects_success(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(implementation, "get_redis_connection_pool", get_queue_pool_mock)
    monkeypatch.setattr(implementation, "Redis", RedisClientMock)
    monkeypatch.setattr(implementation, "AsyncSearchIndex", AsyncSearchIndexMock)

    async with RedisVectorDB() as db:
        await db.delete_objects(
            index_name="test_index",
            ids=["key1", "key2"],
        )

        assert True

@pytest.mark.asyncio
async def test_redis_vector_db_delete_objects_failure(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(implementation, "get_redis_connection_pool", get_queue_pool_mock)
    monkeypatch.setattr(implementation, "Redis", RedisClientMock)
    monkeypatch.setattr(implementation, "AsyncSearchIndex", AsyncSearchIndexDeleteObjectsFailedMock)

    async with RedisVectorDB() as db:
        with pytest.raises(expected_exception=DeleteObjectsException, match="Failed to delete objects"):
            await db.delete_objects(
                index_name="test_index",
                ids=["key1", "key2"],
            )

@pytest.mark.asyncio
async def test_redis_vector_db_semantic_search(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(implementation, "get_redis_connection_pool", get_queue_pool_mock)
    monkeypatch.setattr(implementation, "Redis", RedisClientMock)
    monkeypatch.setattr(implementation, "AsyncSearchIndex", AsyncSearchIndexMock)

    max_results: int = 5
    score_threshold: float = 0.6

    async with RedisVectorDB() as db:
        results = await db.semantic_search(
            index_name="test_index",
            embedding_query=[0.1] * 128,
            max_results=max_results,
            score_threshold=score_threshold,
        )

        assert isinstance(results, list)
        assert all(result.score >= score_threshold and result.score <= 1.0 for result in results)
        assert len(results) <= max_results

def test_get_redis_vector_db(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(implementation, "get_redis_connection_pool", get_queue_pool_mock)

    redis_vector_db: RedisVectorDB = get_redis_vector_db()

    assert isinstance(redis_vector_db, RedisVectorDB)
