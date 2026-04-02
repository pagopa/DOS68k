import pytest

from typing import List

from dos_utility.vector_db import ObjectData
from dos_utility.vector_db.qdrant import implementation
from dos_utility.vector_db.qdrant import QdrantVectorDB, get_qdrant_vector_db
from dos_utility.vector_db.qdrant.env import get_qdrant_vector_db_settings
from dos_utility.vector_db.exceptions import IndexCreationException, IndexDeletionException, PutObjectsException, DeleteObjectsException
from llama_index.core.vector_stores.types import (
    VectorStoreQuery, VectorStoreQueryResult,
    MetadataFilters, MetadataFilter, FilterOperator, FilterCondition,
)

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
                    vector=[0.1] * 128,
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
                    vector=[0.1] * 128,
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
                        vector=[0.1] * 128,
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

def test_qdrant_client_property(monkeypatch: pytest.MonkeyPatch):
    get_qdrant_vector_db_settings.cache_clear()

    monkeypatch.setattr(implementation, "get_qdrant_vector_db_settings", get_qdrant_vector_db_settings_mock)
    monkeypatch.setattr(implementation, "AsyncQdrantClient", AsyncQdrantClientMock)

    db = QdrantVectorDB()
    assert isinstance(db.client, AsyncQdrantClientMock)

def test_get_qdrant_vector_db(monkeypatch: pytest.MonkeyPatch):
    get_qdrant_vector_db_settings.cache_clear()

    monkeypatch.setattr(implementation, "get_qdrant_vector_db_settings", get_qdrant_vector_db_settings_mock)

    qdrant_db: QdrantVectorDB = get_qdrant_vector_db()

    assert isinstance(qdrant_db, QdrantVectorDB)

@pytest.mark.asyncio
async def test_semantic_search_with_filters(monkeypatch: pytest.MonkeyPatch):
    get_qdrant_vector_db_settings.cache_clear()

    monkeypatch.setattr(implementation, "get_qdrant_vector_db_settings", get_qdrant_vector_db_settings_mock)
    monkeypatch.setattr(implementation, "AsyncQdrantClient", AsyncQdrantClientMock)

    async with QdrantVectorDB() as db:
        results = await db.semantic_search(
            index_name="test_index",
            embedding_query=[0.1] * 128,
            max_results=5,
            score_threshold=0.6,
            filters=MetadataFilters(filters=[MetadataFilter(key="filename", value="file1.txt")]),
        )

    assert isinstance(results, list)

@pytest.mark.asyncio
async def test_filter_search(monkeypatch: pytest.MonkeyPatch):
    get_qdrant_vector_db_settings.cache_clear()

    monkeypatch.setattr(implementation, "get_qdrant_vector_db_settings", get_qdrant_vector_db_settings_mock)
    monkeypatch.setattr(implementation, "AsyncQdrantClient", AsyncQdrantClientMock)

    async with QdrantVectorDB() as db:
        results = await db.filter_search(
            index_name="test_index",
            filters=MetadataFilters(filters=[MetadataFilter(key="filename", value="file1.txt")]),
            max_results=5,
        )

    assert isinstance(results, list)
    assert all(r.score is None for r in results)

@pytest.mark.asyncio
async def test_filter_search_ne_operator(monkeypatch: pytest.MonkeyPatch):
    get_qdrant_vector_db_settings.cache_clear()

    monkeypatch.setattr(implementation, "get_qdrant_vector_db_settings", get_qdrant_vector_db_settings_mock)
    monkeypatch.setattr(implementation, "AsyncQdrantClient", AsyncQdrantClientMock)

    async with QdrantVectorDB() as db:
        results = await db.filter_search(
            index_name="test_index",
            filters=MetadataFilters(filters=[MetadataFilter(key="filename", value="file1.txt", operator=FilterOperator.NE)]),
            max_results=5,
        )

    assert isinstance(results, list)

@pytest.mark.asyncio
async def test_filter_search_nin_operator(monkeypatch: pytest.MonkeyPatch):
    get_qdrant_vector_db_settings.cache_clear()

    monkeypatch.setattr(implementation, "get_qdrant_vector_db_settings", get_qdrant_vector_db_settings_mock)
    monkeypatch.setattr(implementation, "AsyncQdrantClient", AsyncQdrantClientMock)

    async with QdrantVectorDB() as db:
        results = await db.filter_search(
            index_name="test_index",
            filters=MetadataFilters(filters=[MetadataFilter(key="filename", value=["file1.txt", "file2.txt"], operator=FilterOperator.NIN)]),
            max_results=5,
        )

    assert isinstance(results, list)

@pytest.mark.asyncio
async def test_filter_search_text_match(monkeypatch: pytest.MonkeyPatch):
    get_qdrant_vector_db_settings.cache_clear()

    monkeypatch.setattr(implementation, "get_qdrant_vector_db_settings", get_qdrant_vector_db_settings_mock)
    monkeypatch.setattr(implementation, "AsyncQdrantClient", AsyncQdrantClientMock)

    async with QdrantVectorDB() as db:
        results = await db.filter_search(
            index_name="test_index",
            filters=MetadataFilters(filters=[MetadataFilter(key="content", value="hello", operator=FilterOperator.TEXT_MATCH)]),
            max_results=5,
        )

    assert isinstance(results, list)

@pytest.mark.asyncio
async def test_filter_search_text_match_insensitive(monkeypatch: pytest.MonkeyPatch):
    get_qdrant_vector_db_settings.cache_clear()

    monkeypatch.setattr(implementation, "get_qdrant_vector_db_settings", get_qdrant_vector_db_settings_mock)
    monkeypatch.setattr(implementation, "AsyncQdrantClient", AsyncQdrantClientMock)

    async with QdrantVectorDB() as db:
        results = await db.filter_search(
            index_name="test_index",
            filters=MetadataFilters(filters=[MetadataFilter(key="content", value="hello", operator=FilterOperator.TEXT_MATCH_INSENSITIVE)]),
            max_results=5,
        )

    assert isinstance(results, list)

@pytest.mark.asyncio
async def test_filter_search_in_operator(monkeypatch: pytest.MonkeyPatch):
    get_qdrant_vector_db_settings.cache_clear()

    monkeypatch.setattr(implementation, "get_qdrant_vector_db_settings", get_qdrant_vector_db_settings_mock)
    monkeypatch.setattr(implementation, "AsyncQdrantClient", AsyncQdrantClientMock)

    async with QdrantVectorDB() as db:
        results = await db.filter_search(
            index_name="test_index",
            filters=MetadataFilters(filters=[MetadataFilter(key="filename", value=["file1.txt", "file2.txt"], operator=FilterOperator.IN)]),
            max_results=5,
        )

    assert isinstance(results, list)

@pytest.mark.asyncio
async def test_filter_search_any_operator(monkeypatch: pytest.MonkeyPatch):
    get_qdrant_vector_db_settings.cache_clear()

    monkeypatch.setattr(implementation, "get_qdrant_vector_db_settings", get_qdrant_vector_db_settings_mock)
    monkeypatch.setattr(implementation, "AsyncQdrantClient", AsyncQdrantClientMock)

    async with QdrantVectorDB() as db:
        results = await db.filter_search(
            index_name="test_index",
            filters=MetadataFilters(filters=[MetadataFilter(key="filename", value="file1.txt", operator=FilterOperator.ANY)]),
            max_results=5,
        )

    assert isinstance(results, list)

@pytest.mark.asyncio
async def test_filter_search_range_operators(monkeypatch: pytest.MonkeyPatch):
    get_qdrant_vector_db_settings.cache_clear()

    monkeypatch.setattr(implementation, "get_qdrant_vector_db_settings", get_qdrant_vector_db_settings_mock)
    monkeypatch.setattr(implementation, "AsyncQdrantClient", AsyncQdrantClientMock)

    async with QdrantVectorDB() as db:
        for op in (FilterOperator.GT, FilterOperator.LT, FilterOperator.GTE, FilterOperator.LTE):
            results = await db.filter_search(
                index_name="test_index",
                filters=MetadataFilters(filters=[MetadataFilter(key="chunk_id", value=5, operator=op)]),
                max_results=5,
            )
            assert isinstance(results, list)

@pytest.mark.asyncio
async def test_filter_search_is_empty(monkeypatch: pytest.MonkeyPatch):
    get_qdrant_vector_db_settings.cache_clear()

    monkeypatch.setattr(implementation, "get_qdrant_vector_db_settings", get_qdrant_vector_db_settings_mock)
    monkeypatch.setattr(implementation, "AsyncQdrantClient", AsyncQdrantClientMock)

    async with QdrantVectorDB() as db:
        results = await db.filter_search(
            index_name="test_index",
            filters=MetadataFilters(filters=[MetadataFilter(key="content", value="", operator=FilterOperator.IS_EMPTY)]),
            max_results=5,
        )

    assert isinstance(results, list)

@pytest.mark.asyncio
async def test_filter_search_or_condition(monkeypatch: pytest.MonkeyPatch):
    get_qdrant_vector_db_settings.cache_clear()

    monkeypatch.setattr(implementation, "get_qdrant_vector_db_settings", get_qdrant_vector_db_settings_mock)
    monkeypatch.setattr(implementation, "AsyncQdrantClient", AsyncQdrantClientMock)

    async with QdrantVectorDB() as db:
        results = await db.filter_search(
            index_name="test_index",
            filters=MetadataFilters(
                condition=FilterCondition.OR,
                filters=[
                    MetadataFilter(key="filename", value="file1.txt"),
                    MetadataFilter(key="filename", value="file2.txt"),
                ],
            ),
            max_results=5,
        )

    assert isinstance(results, list)

@pytest.mark.asyncio
async def test_filter_search_or_condition_with_ne(monkeypatch: pytest.MonkeyPatch):
    get_qdrant_vector_db_settings.cache_clear()

    monkeypatch.setattr(implementation, "get_qdrant_vector_db_settings", get_qdrant_vector_db_settings_mock)
    monkeypatch.setattr(implementation, "AsyncQdrantClient", AsyncQdrantClientMock)

    async with QdrantVectorDB() as db:
        results = await db.filter_search(
            index_name="test_index",
            filters=MetadataFilters(
                condition=FilterCondition.OR,
                filters=[
                    MetadataFilter(key="filename", value="file1.txt", operator=FilterOperator.NE),
                ],
            ),
            max_results=5,
        )

    assert isinstance(results, list)

@pytest.mark.asyncio
async def test_filter_search_nested_filters(monkeypatch: pytest.MonkeyPatch):
    get_qdrant_vector_db_settings.cache_clear()

    monkeypatch.setattr(implementation, "get_qdrant_vector_db_settings", get_qdrant_vector_db_settings_mock)
    monkeypatch.setattr(implementation, "AsyncQdrantClient", AsyncQdrantClientMock)

    async with QdrantVectorDB() as db:
        results = await db.filter_search(
            index_name="test_index",
            filters=MetadataFilters(filters=[
                MetadataFilters(filters=[MetadataFilter(key="filename", value="file1.txt")]),
            ]),
            max_results=5,
        )

    assert isinstance(results, list)

@pytest.mark.asyncio
async def test_filter_search_nested_empty_returns_none(monkeypatch: pytest.MonkeyPatch):
    get_qdrant_vector_db_settings.cache_clear()

    monkeypatch.setattr(implementation, "get_qdrant_vector_db_settings", get_qdrant_vector_db_settings_mock)
    monkeypatch.setattr(implementation, "AsyncQdrantClient", AsyncQdrantClientMock)

    # Nested empty MetadataFilters → _build_filter_condition returns None (no positive, no negative)
    async with QdrantVectorDB() as db:
        results = await db.filter_search(
            index_name="test_index",
            filters=MetadataFilters(filters=[MetadataFilters(filters=[])]),
            max_results=5,
        )

    assert isinstance(results, list)

@pytest.mark.asyncio
async def test_semantic_search_with_empty_filters(monkeypatch: pytest.MonkeyPatch):
    get_qdrant_vector_db_settings.cache_clear()

    monkeypatch.setattr(implementation, "get_qdrant_vector_db_settings", get_qdrant_vector_db_settings_mock)
    monkeypatch.setattr(implementation, "AsyncQdrantClient", AsyncQdrantClientMock)

    async with QdrantVectorDB() as db:
        results = await db.semantic_search(
            index_name="test_index",
            embedding_query=[0.1] * 128,
            max_results=5,
            score_threshold=0.0,
            filters=MetadataFilters(filters=[]),
        )

    assert isinstance(results, list)

@pytest.mark.asyncio
async def test_aquery_with_embedding(monkeypatch: pytest.MonkeyPatch):
    get_qdrant_vector_db_settings.cache_clear()

    monkeypatch.setattr(implementation, "get_qdrant_vector_db_settings", get_qdrant_vector_db_settings_mock)
    monkeypatch.setattr(implementation, "AsyncQdrantClient", AsyncQdrantClientMock)

    db = QdrantVectorDB(index_name="test_index")
    result = await db.aquery(VectorStoreQuery(query_embedding=[0.1] * 128, similarity_top_k=5))

    assert isinstance(result, VectorStoreQueryResult)
    assert result.similarities is not None

@pytest.mark.asyncio
async def test_aquery_filter_only(monkeypatch: pytest.MonkeyPatch):
    get_qdrant_vector_db_settings.cache_clear()

    monkeypatch.setattr(implementation, "get_qdrant_vector_db_settings", get_qdrant_vector_db_settings_mock)
    monkeypatch.setattr(implementation, "AsyncQdrantClient", AsyncQdrantClientMock)

    db = QdrantVectorDB(index_name="test_index")
    result = await db.aquery(VectorStoreQuery(
        filters=MetadataFilters(filters=[MetadataFilter(key="filename", value="file1.txt")]),
        similarity_top_k=5,
    ))

    assert isinstance(result, VectorStoreQueryResult)
    assert result.similarities is None

@pytest.mark.asyncio
async def test_aquery_no_index_name(monkeypatch: pytest.MonkeyPatch):
    get_qdrant_vector_db_settings.cache_clear()

    monkeypatch.setattr(implementation, "get_qdrant_vector_db_settings", get_qdrant_vector_db_settings_mock)
    monkeypatch.setattr(implementation, "AsyncQdrantClient", AsyncQdrantClientMock)

    db = QdrantVectorDB()
    with pytest.raises(ValueError, match="index_name must be set at construction time"):
        await db.aquery(VectorStoreQuery(query_embedding=[0.1] * 128, similarity_top_k=5))

@pytest.mark.asyncio
async def test_aquery_no_embedding_no_filters(monkeypatch: pytest.MonkeyPatch):
    get_qdrant_vector_db_settings.cache_clear()

    monkeypatch.setattr(implementation, "get_qdrant_vector_db_settings", get_qdrant_vector_db_settings_mock)
    monkeypatch.setattr(implementation, "AsyncQdrantClient", AsyncQdrantClientMock)

    db = QdrantVectorDB(index_name="test_index")
    with pytest.raises(ValueError, match="Either query_embedding or filters must be provided"):
        await db.aquery(VectorStoreQuery(similarity_top_k=5))
