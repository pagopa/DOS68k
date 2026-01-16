import pytest

from typing import Generator
from redis.asyncio import ConnectionPool, Redis

from dos_utility.queue.redis import connection
from dos_utility.queue.redis.connection import get_queue_pool, get_queue_client

from test.queue.redis.mocks import ConnectionPoolMock, RedisMock, get_queue_pool_mock


def test_get_queue_pool(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(connection, "ConnectionPool", ConnectionPoolMock)

    pool: ConnectionPool = get_queue_pool()
    assert isinstance(pool, ConnectionPool)

def test_get_queue_client(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(connection, "get_queue_pool", get_queue_pool_mock)
    monkeypatch.setattr(connection, "Redis", RedisMock)

    gen: Generator = get_queue_client()
    client: Redis = next(gen)

    assert isinstance(client, Redis)
