import pytest

from typing import AsyncGenerator
from redis.asyncio import ConnectionPool, Redis

from dos_utility.queue.redis import connection
from dos_utility.queue.redis.connection import get_queue_pool, get_queue_client, get_queue_client_ctx

from test.queue.redis.mocks import ConnectionPoolMock, RedisMock, get_queue_pool_mock


def test_get_queue_pool(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(connection, "ConnectionPool", ConnectionPoolMock)

    pool: ConnectionPool = get_queue_pool()
    assert isinstance(pool, ConnectionPool)

@pytest.mark.asyncio
async def test_get_queue_client(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(connection, "get_queue_pool", get_queue_pool_mock)
    monkeypatch.setattr(connection, "Redis", RedisMock)

    gen: AsyncGenerator = get_queue_client()
    client: Redis = await gen.__anext__()

    assert isinstance(client, Redis)

@pytest.mark.asyncio
async def test_get_queue_client_(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(connection, "get_queue_pool", get_queue_pool_mock)
    monkeypatch.setattr(connection, "Redis", RedisMock)

    async with get_queue_client_ctx() as client:
        assert isinstance(client, Redis)