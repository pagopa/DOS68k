import pytest
import pytest_asyncio
import asyncio

from typing import Tuple
from fastapi import FastAPI
from httpx import AsyncClient, ASGITransport
from sqlalchemy.pool import StaticPool
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, AsyncSession
from sqlalchemy.orm import sessionmaker

from test.routers.mocks import QueueMock


@pytest.fixture(scope="function")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture(scope="function")
async def engine():
    # In-memory SQLite
    eng: AsyncEngine = create_async_engine(url="sqlite+aiosqlite:///:memory:", poolclass=StaticPool, future=True)

    # # Create tables
    # async with eng.begin() as conn:
    #     await conn.run_sync(Base.metadata.create_all)

    try:
        yield eng
    finally:
        await eng.dispose()

# AsyncSession for tests
@pytest_asyncio.fixture
async def session(engine: AsyncEngine):
    session_local = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

    async with session_local() as s:
        yield s
        await s.rollback() # Per isolamento tra i test

@pytest_asyncio.fixture
async def app_test(session: AsyncSession):
    from src.main import app
    from dos_utility.database.sql import get_async_session
    from dos_utility.queue import get_queue_client

    # Override dependencies or setup test-specific configurations here if needed

    async def override_get_db_session():
        yield session

    redis_mock: QueueMock = QueueMock(ping_response=True)
    async def override_get_queue_client():
        # Return a RedisMock instance for testing
        return redis_mock

    app.dependency_overrides[get_async_session] = override_get_db_session
    app.dependency_overrides[get_queue_client] = override_get_queue_client

    try:
        yield app, redis_mock
    finally:
        app.dependency_overrides.clear()

@pytest_asyncio.fixture
async def client_test(app_test: Tuple[FastAPI, QueueMock]):
    app, queue_client = app_test
    # Async client for testing FastAPI app
    async with AsyncClient(base_url="http://testserver", transport=ASGITransport(app=app)) as client:
        yield client, queue_client
