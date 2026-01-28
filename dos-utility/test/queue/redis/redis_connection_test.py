import pytest

from redis.asyncio import ConnectionPool

from dos_utility.queue.redis import connection
from dos_utility.queue.redis.connection import get_queue_pool

from test.queue.redis.mocks import ConnectionPoolMock


def test_get_queue_pool(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(connection, "ConnectionPool", ConnectionPoolMock)

    pool: ConnectionPool = get_queue_pool()
    assert isinstance(pool, ConnectionPool)
