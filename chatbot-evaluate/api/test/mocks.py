from typing import Self

class QueueMock:
    def __init__(self: Self):
        self.healthy: bool = True

    async def is_healthy(self: Self) -> bool:
        return self.healthy
