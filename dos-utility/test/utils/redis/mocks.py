from typing import Optional
from redis.asyncio import ConnectionPool


class ConnectionPoolMock(ConnectionPool):
    @classmethod
    def from_url(cls, *args, **kwargs) -> ConnectionPool:
        return cls()

def get_queue_pool_mock(decode_responses: Optional[bool]=None) -> ConnectionPool:
    return ConnectionPoolMock()

class RedisConnectionSettingsMock:
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379

def get_redis_connection_settings_mock() -> RedisConnectionSettingsMock:
    return RedisConnectionSettingsMock()