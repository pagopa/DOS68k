import pytest

from dos_utility.queue.sqs import implementation
from dos_utility.queue.sqs import SQSQueue, get_sqs_queue
from dos_utility.queue.sqs.env import get_sqs_queue_settings

from test.queue.sqs.mocks import (
    boto3_client_mock,
    boto3_client_unhealthy_mock,
    boto3_client_new_message_dequeue_mock,
)



def test_instantiate_sqs_queue(monkeypatch: pytest.MonkeyPatch):
    get_sqs_queue_settings.cache_clear()
    
    monkeypatch.setenv("SQS_QUEUE_NAME", "my-queue")
    monkeypatch.setenv("SQS_QUEUE_URL", "http://test-queue-url")

    sqs_queue: SQSQueue = SQSQueue()

    assert isinstance(sqs_queue, SQSQueue)

@pytest.mark.asyncio
async def test_sqs_aenter_aexit(monkeypatch: pytest.MonkeyPatch):
    get_sqs_queue_settings.cache_clear()

    monkeypatch.setattr(implementation.boto3, "client", boto3_client_mock)
    monkeypatch.setenv("SQS_QUEUE_NAME", "my-queue")
    monkeypatch.setenv("SQS_QUEUE_URL", "http://test-queue-url")


    async with SQSQueue() as sqs_queue:
        assert isinstance(sqs_queue, SQSQueue)

@pytest.mark.asyncio
async def test_sqs_is_healthy(monkeypatch: pytest.MonkeyPatch):
    get_sqs_queue_settings.cache_clear()

    monkeypatch.setattr(implementation.boto3, "client", boto3_client_mock)
    monkeypatch.setenv("SQS_QUEUE_NAME", "my-queue")
    monkeypatch.setenv("SQS_QUEUE_URL", "http://test-queue-url")

    async with SQSQueue() as sqs_queue:
        is_healthy: bool = await sqs_queue.is_healthy()

        assert is_healthy is True

@pytest.mark.asyncio
async def test_sqs_is_unhealthy(monkeypatch: pytest.MonkeyPatch):
    get_sqs_queue_settings.cache_clear()

    monkeypatch.setattr(implementation.boto3, "client", boto3_client_unhealthy_mock)
    monkeypatch.setenv("SQS_QUEUE_NAME", "my-queue")
    monkeypatch.setenv("SQS_QUEUE_URL", "http://test-queue-url")

    async with SQSQueue() as sqs_queue:
        is_healthy: bool = await sqs_queue.is_healthy()

        assert is_healthy is False

@pytest.mark.asyncio
async def test_sqs_enqueue(monkeypatch: pytest.MonkeyPatch):
    get_sqs_queue_settings.cache_clear()

    monkeypatch.setattr(implementation.boto3, "client", boto3_client_mock)
    monkeypatch.setenv("SQS_QUEUE_NAME", "my-queue")
    monkeypatch.setenv("SQS_QUEUE_URL", "http://test-queue-url")

    async with SQSQueue() as sqs_queue:
        msg_id: str = await sqs_queue.enqueue(b"test-message")

        assert isinstance(msg_id, str)

@pytest.mark.asyncio
async def test_sqs_dequeue_no_message(monkeypatch: pytest.MonkeyPatch):
    get_sqs_queue_settings.cache_clear()

    monkeypatch.setattr(implementation.boto3, "client", boto3_client_mock)
    monkeypatch.setenv("SQS_QUEUE_NAME", "my-queue")
    monkeypatch.setenv("SQS_QUEUE_URL", "http://test-queue-url")

    async with SQSQueue() as sqs_queue:
        msg, msg_id = await sqs_queue.dequeue()

        assert msg is None
        assert msg_id is None

@pytest.mark.asyncio
async def test_sqs_dequeue_new_message(monkeypatch: pytest.MonkeyPatch):
    get_sqs_queue_settings.cache_clear()

    monkeypatch.setattr(implementation.boto3, "client", boto3_client_new_message_dequeue_mock)
    monkeypatch.setenv("SQS_QUEUE_NAME", "my-queue")
    monkeypatch.setenv("SQS_QUEUE_URL", "http://test-queue-url")

    async with SQSQueue() as sqs_queue:
        msg, msg_id = await sqs_queue.dequeue()

        assert isinstance(msg, bytes)
        assert isinstance(msg_id, str)

@pytest.mark.asyncio
async def test_sqs_acknowledge(monkeypatch: pytest.MonkeyPatch):
    get_sqs_queue_settings.cache_clear()

    monkeypatch.setattr(implementation.boto3, "client", boto3_client_mock)
    monkeypatch.setenv("SQS_QUEUE_NAME", "my-queue")
    monkeypatch.setenv("SQS_QUEUE_URL", "http://test-queue-url")

    async with SQSQueue() as sqs_queue:
        await sqs_queue.acknowledge("mocked-msg-id")

        assert True

def test_get_sqs_queue(monkeypatch: pytest.MonkeyPatch):
    get_sqs_queue_settings.cache_clear()
    monkeypatch.setenv("SQS_QUEUE_NAME", "my-queue")
    monkeypatch.setenv("SQS_QUEUE_URL", "http://test-queue-url")

    sqs_queue: SQSQueue = get_sqs_queue()

    assert isinstance(sqs_queue, SQSQueue)