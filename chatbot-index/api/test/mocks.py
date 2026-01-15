from typing import Literal

class RedisMock:
    # Mock Redis client for testing
    def __init__(self, ping_response: bool | Literal["exception"]=True):
        self.ping_response: bool | Literal["exception"] = ping_response # Set the desired ping response

    async def ping(self) -> bool:
        if self.ping_response == "exception":
            raise Exception("Mocked queue connection error")

        return self.ping_response

class AWSS3ConnectedMock:
    def __init__(self, *args, **kwargs):
        return

    def health_check(self, *args, **kwargs) -> None:
        return

class AWSS3ExceptionMock:
    def __init__(self, *args, **kwargs):
        return

    def health_check(self, *args, **kwargs) -> None:
        raise Exception("Mocked storage connection error")
