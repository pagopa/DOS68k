import pytest

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from dos_utility.database.sql import connection
from dos_utility.database.sql.connection import get_async_engine, get_async_session

from test.database.sql.mocks import URLMock, create_async_engine_mock, sessionmakerMock, get_async_engine_mock

def test_get_async_engine(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(connection, "URL", URLMock)
    monkeypatch.setattr(connection, "create_async_engine", create_async_engine_mock)

    async_engine: AsyncEngine = get_async_engine()

    assert isinstance(async_engine, AsyncEngine)

@pytest.mark.asyncio
async def test_get_async_session(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(connection, "get_async_engine", get_async_engine_mock)
    monkeypatch.setattr(connection, "sessionmaker", sessionmakerMock)

    async for session in get_async_session():
        assert isinstance(session, AsyncSession)
