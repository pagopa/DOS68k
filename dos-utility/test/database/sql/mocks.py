from sqlalchemy.engine.url import URL
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from sqlalchemy.orm import sessionmaker

class URLMock(URL):
    def __new__(cls, *args, **kwargs):
        pass

    @classmethod
    def create(cls, *args, **kwargs) -> URL:
        return cls() # It calls __new__

class AsyncEngineMock(AsyncEngine):
    def __init__(self, *args, **kwargs):
        pass

class AsyncSessionMock(AsyncSession):
    async def __aenter__(self, *args, **kwargs):
        return self

    async def __aexit__(self, *args, **kwargs):
        pass

class sessionmakerMock(sessionmaker):
    def __init__(self, *args, **kwargs):
        pass

    def __call__(self, **local_kw):
        return AsyncSessionMock()

def create_async_engine_mock(*args, **kwargs) -> AsyncEngine:
    return AsyncEngineMock()

def get_async_engine_mock() -> AsyncEngine:
    return create_async_engine_mock()
