import pytest

from fastapi import HTTPException

from src.modules.index.service import IndexService
from src.modules.index.dto import CreateIndexResponse

from test.modules.index.mocks import (
    MOCK_USER_ID,
    MOCK_INDEX_ID,
    MOCK_EXISTING_INDEXES,
    MockStorage,
    MockVectorDBWithIndexes,
    MockVectorDBEmpty,
    MockVectorDBCreateFails,
    MockVectorDBDeleteFails,
)


@pytest.fixture(autouse=True)
def setup_env(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("EMBED_DIM", "768")
    monkeypatch.setenv("INDEX_DOCUMENTS_BUCKET_NAME", "test-bucket")

    from src.env import get_index_bucket_settings, get_settings
    from src.modules.index.env import get_embedding_settings

    get_index_bucket_settings.cache_clear()
    get_settings.cache_clear()
    get_embedding_settings.cache_clear()


# ---------------------------------------------------------------------------
# create_index
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_index_success():
    vdb = MockVectorDBEmpty()
    service = IndexService(vdb=vdb, storage=MockStorage())

    result: CreateIndexResponse = await service.create_index(
        index_id=MOCK_INDEX_ID, user_id=MOCK_USER_ID
    )

    assert result.index_id == MOCK_INDEX_ID
    assert str(result.user_id) == MOCK_USER_ID
    assert result.created_at is not None


@pytest.mark.asyncio
async def test_create_index_already_exists():
    vdb = MockVectorDBWithIndexes()
    service = IndexService(vdb=vdb, storage=MockStorage())

    existing_id = MOCK_EXISTING_INDEXES[0]

    with pytest.raises(
        expected_exception=HTTPException, match="Index already exists"
    ) as exc_info:
        await service.create_index(index_id=existing_id, user_id=MOCK_USER_ID)

    assert exc_info.value.status_code == 409


@pytest.mark.asyncio
async def test_create_index_vdb_failure():
    vdb = MockVectorDBCreateFails()
    service = IndexService(vdb=vdb, storage=MockStorage())

    with pytest.raises(expected_exception=HTTPException) as exc_info:
        await service.create_index(index_id=MOCK_INDEX_ID, user_id=MOCK_USER_ID)

    assert exc_info.value.status_code == 500


# ---------------------------------------------------------------------------
# delete_index
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_delete_index_success():
    vdb = MockVectorDBWithIndexes()
    service = IndexService(vdb=vdb, storage=MockStorage())

    existing_id = MOCK_EXISTING_INDEXES[0]

    await service.delete_index(index_id=existing_id)

    remaining = await vdb.get_indexes()
    assert existing_id not in remaining


@pytest.mark.asyncio
async def test_delete_index_removes_storage_objects():
    existing_id = MOCK_EXISTING_INDEXES[0]
    storage = MockStorage(initial_objects=[f"{existing_id}/doc.pdf", "other/doc.txt"])
    vdb = MockVectorDBWithIndexes()
    service = IndexService(vdb=vdb, storage=storage)

    await service.delete_index(index_id=existing_id)

    remaining = [o.key for o in storage.list_objects(bucket="test-bucket")]
    assert f"{existing_id}/doc.pdf" not in remaining
    assert "other/doc.txt" in remaining


@pytest.mark.asyncio
async def test_delete_index_not_found():
    vdb = MockVectorDBEmpty()
    service = IndexService(vdb=vdb, storage=MockStorage())

    with pytest.raises(
        expected_exception=HTTPException,
        match="404: Index 'nonexistent' does not exist",
    ) as exc_info:
        await service.delete_index(index_id="nonexistent")

    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_delete_index_vdb_failure():
    vdb = MockVectorDBDeleteFails()
    service = IndexService(vdb=vdb, storage=MockStorage())

    existing_id = MOCK_EXISTING_INDEXES[0]

    with pytest.raises(expected_exception=HTTPException) as exc_info:
        await service.delete_index(index_id=existing_id)

    assert exc_info.value.status_code == 500


# ---------------------------------------------------------------------------
# get_indexes
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_indexes_returns_list():
    vdb = MockVectorDBWithIndexes()
    service = IndexService(vdb=vdb, storage=MockStorage())

    result = await service.get_indexes()

    assert result == MOCK_EXISTING_INDEXES


@pytest.mark.asyncio
async def test_get_indexes_returns_empty():
    vdb = MockVectorDBEmpty()
    service = IndexService(vdb=vdb, storage=MockStorage())

    result = await service.get_indexes()

    assert result == []


# ---------------------------------------------------------------------------
# get_index_service (DI factory)
# ---------------------------------------------------------------------------


def test_get_index_service_factory():
    from src.modules.index.service import get_index_service

    result = get_index_service(vdb=MockVectorDBEmpty(), storage=MockStorage())

    assert isinstance(result, IndexService)
