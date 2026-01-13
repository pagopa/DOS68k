import pytest
import pytest_asyncio
import asyncio

from fastapi import FastAPI
from httpx import AsyncClient, ASGITransport
from sqlalchemy.pool import StaticPool
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, AsyncSession
from sqlalchemy.orm import sessionmaker


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
    from src.db import get_db_session

    # Override dependencies or setup test-specific configurations here if needed

    async def override_get_db_session():
        yield session

    app.dependency_overrides[get_db_session] = override_get_db_session

    try:
        yield app
    finally:
        app.dependency_overrides.clear()

@pytest_asyncio.fixture
async def client_test(app_test: FastAPI):
    # Async client for testing FastAPI app
    async with AsyncClient(base_url="http://testserver", transport=ASGITransport(app=app_test)) as client:
        yield client