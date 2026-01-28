from typing import Literal, Self

class QueueMock:
    # Mock Queue client for testing
    def __init__(self, ping_response: bool | Literal["exception"]=True):
        self.ping_response: bool | Literal["exception"] = ping_response # Set the desired ping response

    async def is_healthy(self: Self) -> bool:
        if self.ping_response == "exception":
            return False

        return self.ping_response
