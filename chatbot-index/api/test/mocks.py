from typing import Literal, Self

class QueueMock:
    # Mock Redis client for testing
    def __init__(self: Self, ping_response: bool | Literal["exception"]=True):
        self.ping_response: bool | Literal["exception"] = ping_response # Set the desired ping response

    async def is_healthy(self: Self) -> bool:
        if self.ping_response == "exception":
            return False

        return self.ping_response

class AWSS3ConnectedMock:
    def __init__(self: Self, *args, **kwargs):
        return

    def health_check(self: Self, *args, **kwargs) -> None:
        return

class AWSS3ExceptionMock:
    def __init__(self: Self, *args, **kwargs):
        return

    def health_check(self: Self, *args, **kwargs) -> None:
        raise Exception("Mocked storage connection error")
