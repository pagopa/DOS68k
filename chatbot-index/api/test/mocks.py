from typing import Self

class QueueMock:
    # Mock Redis client for testing
    def __init__(self: Self):
        self.healthy: bool = True

    async def is_healthy(self: Self) -> bool:
        return self.healthy

class StorageMock:
    def __init__(self: Self):
        self.healthy: bool = True

    def is_healthy(self: Self) -> bool:
        return self.healthy
