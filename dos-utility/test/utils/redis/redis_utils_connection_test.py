import pytest

from redis.asyncio import ConnectionPool

from dos_utility.utils.redis import connection, get_redis_connection_pool

from test.utils.redis.mocks import ConnectionPoolMock, get_redis_connection_settings_mock


def test_get_redis_connection_pool_no_decode_responses_param(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(connection, "ConnectionPool", ConnectionPoolMock)
    monkeypatch.setattr(connection, "get_redis_connection_settings", get_redis_connection_settings_mock)

    pool: ConnectionPool = get_redis_connection_pool()
    assert isinstance(pool, ConnectionPool)

@pytest.mark.parametrize("decode_responses", [True, False])
def test_get_redis_connection_pool_decode_responses_param(monkeypatch: pytest.MonkeyPatch, decode_responses: bool):
    monkeypatch.setattr(connection, "ConnectionPool", ConnectionPoolMock)
    monkeypatch.setattr(connection, "get_redis_connection_settings", get_redis_connection_settings_mock)

    pool: ConnectionPool = get_redis_connection_pool(decode_responses=decode_responses)
    assert isinstance(pool, ConnectionPool)
