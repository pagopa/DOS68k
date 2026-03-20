import pytest

from typing import AsyncGenerator

from dos_utility import vector_db
from dos_utility.vector_db.interface import VectorDBInterface
from dos_utility.vector_db.env import get_vector_db_settings

from test.vector_db.mocks import (
    get_vector_db_settings_qdrant_mock,
    get_vector_db_settings_redis_mock,
    get_qdrant_vector_db_mock,
    get_redis_vector_db_mock,
)

@pytest.mark.asyncio
async def test_vector_db_ctx_qdrant(monkeypatch: pytest.MonkeyPatch):
    get_vector_db_settings.cache_clear()

    monkeypatch.setattr(vector_db, "get_vector_db_settings", get_vector_db_settings_qdrant_mock)
    monkeypatch.setattr(vector_db, "get_qdrant_vector_db", get_qdrant_vector_db_mock)

    async with vector_db.get_vector_db_ctx() as vdb:
        assert isinstance(vdb, type(get_qdrant_vector_db_mock()))

@pytest.mark.asyncio
async def test_vector_db_ctx_redis(monkeypatch: pytest.MonkeyPatch):
    get_vector_db_settings.cache_clear()

    monkeypatch.setattr(vector_db, "get_vector_db_settings", get_vector_db_settings_redis_mock)
    monkeypatch.setattr(vector_db, "get_redis_vector_db", get_redis_vector_db_mock)

    async with vector_db.get_vector_db_ctx() as vdb:
        assert isinstance(vdb, type(get_redis_vector_db_mock()))

@pytest.mark.asyncio
async def test_get_vector_db_qdrant(monkeypatch: pytest.MonkeyPatch):
    get_vector_db_settings.cache_clear()

    monkeypatch.setattr(vector_db, "get_vector_db_settings", get_vector_db_settings_qdrant_mock)
    monkeypatch.setattr(vector_db, "get_qdrant_vector_db", get_qdrant_vector_db_mock)

    vector_db_gen: AsyncGenerator = vector_db.get_vector_db()
    vdb: VectorDBInterface = await vector_db_gen.__anext__()

    assert isinstance(vdb, VectorDBInterface)

@pytest.mark.asyncio
async def test_get_vector_db_redis(monkeypatch: pytest.MonkeyPatch):
    get_vector_db_settings.cache_clear()

    monkeypatch.setattr(vector_db, "get_vector_db_settings", get_vector_db_settings_redis_mock)
    monkeypatch.setattr(vector_db, "get_redis_vector_db", get_redis_vector_db_mock)

    vector_db_gen: AsyncGenerator = vector_db.get_vector_db()
    vdb: VectorDBInterface = await vector_db_gen.__anext__()

    assert isinstance(vdb, VectorDBInterface)