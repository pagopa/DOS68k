import pytest

from redis import ResponseError

from src.dos_utility.queue.redis import implementation
from src.dos_utility.queue.redis import RedisQueue, get_redis_queue
from src.dos_utility.queue.redis.env import get_redis_queue_settings

from test.queue.redis.mocks import (
    get_queue_pool_mock,
    RedisMock, 
    RedisGroupAlreadyExistsMock,
    RedisUnexpectedResponseErrorMock,
    RedisUnhealthyMock,
    RedisDequeueNewMessageMock,
)



def test_instantiate_redis_queue():
    get_redis_queue_settings.cache_clear()
    redis_queue: RedisQueue = RedisQueue()

    assert isinstance(redis_queue, RedisQueue)

@pytest.mark.asyncio
async def test_redis_aenter_aexit(monkeypatch: pytest.MonkeyPatch):
    get_redis_queue_settings.cache_clear()

    monkeypatch.setattr(implementation, "Redis", RedisMock)
    monkeypatch.setattr(implementation, "get_queue_pool", get_queue_pool_mock)

    async with RedisQueue() as redis_queue:
        assert isinstance(redis_queue, RedisQueue)

@pytest.mark.asyncio
async def test_redis_already_existing_group(monkeypatch: pytest.MonkeyPatch):
    get_redis_queue_settings.cache_clear()

    monkeypatch.setattr(implementation, "Redis", RedisGroupAlreadyExistsMock)
    monkeypatch.setattr(implementation, "get_queue_pool", get_queue_pool_mock)

    async with RedisQueue() as redis_queue:
        assert isinstance(redis_queue, RedisQueue)

@pytest.mark.asyncio
async def test_redis_unexpected_response_error(monkeypatch: pytest.MonkeyPatch):
    get_redis_queue_settings.cache_clear()

    monkeypatch.setattr(implementation, "Redis", RedisUnexpectedResponseErrorMock)
    monkeypatch.setattr(implementation, "get_queue_pool", get_queue_pool_mock)

    with pytest.raises(expected_exception=ResponseError):
        async with RedisQueue():
            pass

@pytest.mark.asyncio
async def test_redis_is_healthy(monkeypatch: pytest.MonkeyPatch):
    get_redis_queue_settings.cache_clear()

    monkeypatch.setattr(implementation, "Redis", RedisMock)
    monkeypatch.setattr(implementation, "get_queue_pool", get_queue_pool_mock)

    async with RedisQueue() as redis_queue:
        is_healthy: bool = await redis_queue.is_healthy()

        assert is_healthy is True

@pytest.mark.asyncio
async def test_redis_is_unhealthy(monkeypatch: pytest.MonkeyPatch):
    get_redis_queue_settings.cache_clear()

    monkeypatch.setattr(implementation, "Redis", RedisUnhealthyMock)
    monkeypatch.setattr(implementation, "get_queue_pool", get_queue_pool_mock)

    async with RedisQueue() as redis_queue:
        is_healthy: bool = await redis_queue.is_healthy()

        assert is_healthy is False

@pytest.mark.asyncio
async def test_redis_enqueue(monkeypatch: pytest.MonkeyPatch):
    get_redis_queue_settings.cache_clear()

    monkeypatch.setattr(implementation, "Redis", RedisMock)
    monkeypatch.setattr(implementation, "get_queue_pool", get_queue_pool_mock)

    async with RedisQueue() as redis_queue:
        msg_id: str = await redis_queue.enqueue(b"test-message")

        assert isinstance(msg_id, str)

@pytest.mark.asyncio
async def test_redis_dequeue_no_message(monkeypatch: pytest.MonkeyPatch):
    get_redis_queue_settings.cache_clear()

    monkeypatch.setattr(implementation, "Redis", RedisMock)
    monkeypatch.setattr(implementation, "get_queue_pool", get_queue_pool_mock)

    async with RedisQueue() as redis_queue:
        msg, msg_id = await redis_queue.dequeue()

        assert msg is None
        assert msg_id is None

@pytest.mark.asyncio
async def test_redis_dequeue_new_message(monkeypatch: pytest.MonkeyPatch):
    get_redis_queue_settings.cache_clear()

    monkeypatch.setattr(implementation, "Redis", RedisDequeueNewMessageMock)
    monkeypatch.setattr(implementation, "get_queue_pool", get_queue_pool_mock)

    async with RedisQueue() as redis_queue:
        msg, msg_id = await redis_queue.dequeue()

        assert isinstance(msg, bytes)
        assert isinstance(msg_id, str)

@pytest.mark.asyncio
async def test_redis_acknowledge(monkeypatch: pytest.MonkeyPatch):
    get_redis_queue_settings.cache_clear()

    monkeypatch.setattr(implementation, "Redis", RedisMock)
    monkeypatch.setattr(implementation, "get_queue_pool", get_queue_pool_mock)

    async with RedisQueue() as redis_queue:
        await redis_queue.acknowledge("mocked-msg-id")

        assert True

def test_get_redis_queue():
    get_redis_queue_settings.cache_clear()
    redis_queue: RedisQueue = get_redis_queue()

    assert isinstance(redis_queue, RedisQueue)
