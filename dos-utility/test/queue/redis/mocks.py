from redis.asyncio import ConnectionPool, Redis


class ConnectionPoolMock(ConnectionPool):
    @classmethod
    def from_url(cls, *args, **kwargs) -> ConnectionPool:
        return cls()

class RedisMock(Redis):
    def __init__(self, *args, **kwargs):
        pass

    async def aclose(self) -> None:
        pass

def get_queue_pool_mock() -> ConnectionPool:
    return ConnectionPoolMock()