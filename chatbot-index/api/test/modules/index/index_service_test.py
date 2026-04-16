import pytest
import os

from fastapi import HTTPException

from src.modules.index.service import IndexService
from src.modules.index.dto import CreateIndexResponse

from test.modules.index.mocks import (
    MOCK_USER_ID,
    MOCK_INDEX_ID,
    MOCK_EXISTING_INDEXES,
    MockVectorDBWithIndexes,
    MockVectorDBEmpty,
    MockVectorDBCreateFails,
    MockVectorDBDeleteFails,
)


@pytest.fixture(autouse=True)
def setup_env(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("EMBED_DIM", "768")


# ---------------------------------------------------------------------------
# create_index
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_index_success():
    vdb = MockVectorDBEmpty()
    service = IndexService(vdb=vdb)

    result: CreateIndexResponse = await service.create_index(
        index_id=MOCK_INDEX_ID, user_id=MOCK_USER_ID
    )

    assert result.index_id == MOCK_INDEX_ID
    assert str(result.user_id) == MOCK_USER_ID
    assert result.created_at is not None


@pytest.mark.asyncio
async def test_create_index_already_exists():
    vdb = MockVectorDBWithIndexes()
    service = IndexService(vdb=vdb)

    existing_id = MOCK_EXISTING_INDEXES[0]

    with pytest.raises(HTTPException) as exc_info:
        await service.create_index(index_id=existing_id, user_id=MOCK_USER_ID)

    assert exc_info.value.status_code == 409
    assert "already exists" in exc_info.value.detail


@pytest.mark.asyncio
async def test_create_index_vdb_failure():
    vdb = MockVectorDBCreateFails()
    service = IndexService(vdb=vdb)

    with pytest.raises(HTTPException) as exc_info:
        await service.create_index(index_id=MOCK_INDEX_ID, user_id=MOCK_USER_ID)

    assert exc_info.value.status_code == 500


# ---------------------------------------------------------------------------
# delete_index
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_delete_index_success():
    vdb = MockVectorDBWithIndexes()
    service = IndexService(vdb=vdb)

    existing_id = MOCK_EXISTING_INDEXES[0]

    await service.delete_index(index_id=existing_id)

    remaining = await vdb.get_indexes()
    assert existing_id not in remaining


@pytest.mark.asyncio
async def test_delete_index_not_found():
    vdb = MockVectorDBEmpty()
    service = IndexService(vdb=vdb)

    with pytest.raises(HTTPException) as exc_info:
        await service.delete_index(index_id="nonexistent")

    assert exc_info.value.status_code == 404
    assert "not found" in exc_info.value.detail


@pytest.mark.asyncio
async def test_delete_index_vdb_failure():
    vdb = MockVectorDBDeleteFails()
    service = IndexService(vdb=vdb)

    existing_id = MOCK_EXISTING_INDEXES[0]

    with pytest.raises(HTTPException) as exc_info:
        await service.delete_index(index_id=existing_id)

    assert exc_info.value.status_code == 500


# ---------------------------------------------------------------------------
# get_indexes
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_indexes_returns_list():
    vdb = MockVectorDBWithIndexes()
    service = IndexService(vdb=vdb)

    result = await service.get_indexes()

    assert result == MOCK_EXISTING_INDEXES


@pytest.mark.asyncio
async def test_get_indexes_returns_empty():
    vdb = MockVectorDBEmpty()
    service = IndexService(vdb=vdb)

    result = await service.get_indexes()

    assert result == []
