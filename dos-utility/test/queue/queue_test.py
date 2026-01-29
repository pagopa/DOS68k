import pytest

from typing import AsyncGenerator, Callable

from dos_utility import queue
from dos_utility.queue import QueueInterface, get_queue_client, get_queue_client_ctx
from dos_utility.queue.env import get_queue_settings

from test.queue.mocks import get_sqs_queue_mock, get_redis_queue_mock


@pytest.mark.asyncio
async def test_queue_interface_not_instantiable(monkeypatch: pytest.MonkeyPatch):
    get_queue_settings.cache_clear()
    monkeypatch.setenv("QUEUE_TYPE", "sqs")

    with pytest.raises(expected_exception=TypeError):
        async with QueueInterface():
            pass

@pytest.mark.asyncio
@pytest.mark.parametrize(
    "queue_type, func_to_mock, get_queue_mock",
    [
        ("sqs", "get_sqs_queue", get_sqs_queue_mock),
        ("redis", "get_redis_queue", get_redis_queue_mock),
    ],
)
async def test_get_queue_client(monkeypatch: pytest.MonkeyPatch, queue_type: str, func_to_mock: str, get_queue_mock: Callable):
    get_queue_settings.cache_clear()
    monkeypatch.setenv("QUEUE_TYPE", queue_type)
    monkeypatch.setattr(queue, func_to_mock, get_queue_mock)

    queue_gen: AsyncGenerator[QueueInterface, None] = get_queue_client()
    client: QueueInterface = await queue_gen.__anext__()

    assert isinstance(client, QueueInterface)

@pytest.mark.asyncio
@pytest.mark.parametrize(
    "queue_type, func_to_mock, get_queue_mock",
    [
        ("sqs", "get_sqs_queue", get_sqs_queue_mock),
        ("redis", "get_redis_queue", get_redis_queue_mock),
    ],
)
async def test_get_queue_client_ctx(monkeypatch: pytest.MonkeyPatch, queue_type: str, func_to_mock: str, get_queue_mock: Callable):
    get_queue_settings.cache_clear()
    monkeypatch.setenv("QUEUE_TYPE", queue_type)
    monkeypatch.setattr(queue, func_to_mock, get_queue_mock)

    async with get_queue_client_ctx() as client:
        assert isinstance(client, QueueInterface)
