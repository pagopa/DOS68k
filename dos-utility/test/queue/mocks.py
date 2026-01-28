from typing import Self, Tuple, Optional
from src.dos_utility.queue import QueueInterface

class MockQueue(QueueInterface):
    async def __aenter__(self: Self) -> Self:
        return self

    async def __aexit__(self: Self, exc_type, exc_value, traceback) -> None:
        pass

    async def is_healthy(self: Self) -> bool:
        return True

    async def enqueue(self: Self, msg: bytes) -> str:
        return "mock"

    async def dequeue(self: Self) -> Tuple[Optional[bytes], Optional[str]]:
        return None, None

    async def acknowledge(self: Self, ack_token: str) -> None:
        pass

class MockSQSQueue(MockQueue):
    pass

def get_sqs_queue_mock() -> MockSQSQueue:
    return MockSQSQueue()

class MockRedisQueue(MockQueue):
    pass

def get_redis_queue_mock() -> MockRedisQueue:
    return MockRedisQueue()