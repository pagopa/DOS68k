from contextlib import asynccontextmanager
from typing import AsyncGenerator, Self, Optional, Tuple


class StopAsyncIteration(Exception):
    pass


class QueueClientMock:
    async def __aenter__(self: Self) -> Self:
        return self

    async def __aexit__(self: Self, exc_type, exc_val, exc_tb) -> None:
        pass

    async def dequeue(self: Self) -> Tuple[Optional[bytes], Optional[str]]:
        return b'{"task": "example"}', "ack_token_example"

    async def acknowledge(self: Self, ack_token: str) -> None:
        pass

class QueueClientLoopMock:
    def __init__(self: Self):
        self._call_count = 0

    async def __aenter__(self: Self) -> Self:
        return self
    
    async def __aexit__(self: Self, exc_type, exc_val, exc_tb) -> None:
        pass

    async def dequeue(self: Self) -> Tuple[Optional[bytes], Optional[str]]:
        return b'{"task": "example"}', "ack_token_example"

    async def acknowledge(self: Self, ack_token: str) -> None:
        self._call_count += 1

        if self._call_count >= 1:
            raise StopAsyncIteration()


@asynccontextmanager
async def get_queue_client_ctx_mock() -> AsyncGenerator[QueueClientMock, None]:
    async with QueueClientMock() as client:
        yield client

@asynccontextmanager
async def get_queue_client_loop_ctx_mock() -> AsyncGenerator[QueueClientLoopMock, None]:
    async with QueueClientLoopMock() as client:
        yield client

async def process_task_block_loop_mock(body: bytes) -> None:
    raise Exception("Simulated processing error")
