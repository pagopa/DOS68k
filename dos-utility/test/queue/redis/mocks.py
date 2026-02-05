from typing import Self, Any
from redis.asyncio import Redis
from redis import ResponseError


class RedisMock(Redis):
    def __init__(self: Self, *args, **kwargs) -> None:
        pass

    async def xgroup_create(self: Self, name: str, groupname: str, id: str, mkstream: bool):
        return None

    async def aclose(self: Self) -> None:
        return None

    async def ping(self: Self) -> bool:
        return True

    async def xadd(self: Self, name: str, fields: Any) -> str:
        return "mocked-msg-id"

    async def xreadgroup(self: Self, groupname: str, consumername: str, streams: Any, count: int, block: int, noack: bool) -> Any:
        return []

    async def xack(self: Self, name: str, groupname: str, *ids: str) -> int:
        return 0

class RedisGroupAlreadyExistsMock(RedisMock):
    async def xgroup_create(self: Self, name: str, groupname: str, id: str, mkstream: bool):
        raise ResponseError("BUSYGROUP Consumer Group name already exists")

class RedisUnexpectedResponseErrorMock(RedisMock):
    async def xgroup_create(self: Self, name: str, groupname: str, id: str, mkstream: bool):
        raise ResponseError("Some unexpected error")

class RedisUnhealthyMock(RedisMock):
    async def ping(self: Self) -> bool:
        raise Exception("Redis is unhealthy")

class RedisDequeueNewMessageMock(RedisMock):
    async def xreadgroup(self: Self, groupname: str, consumername: str, streams: Any, count: int, block: int, noack: bool) -> Any:
        return [
            (
                "mocked-stream",
                [
                    ("mocked-msg-id", {b"body": b"test-message"})
                ]
            )
        ]

class RedisQueueSettingsMock(RedisMock):
    REDIS_STREAM: str = "mocked-stream"
    REDIS_GROUP: str = "mocked-group"

def get_redis_queue_settings_mock() -> RedisQueueSettingsMock:
    return RedisQueueSettingsMock()