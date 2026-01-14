import pytest
import pytest_asyncio
import asyncio

from typing import Tuple
from fastapi import FastAPI
from httpx import AsyncClient, ASGITransport

from test.mocks import RedisMock


@pytest.fixture(scope="function")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture
async def app_test():
    from src.main import app
    from src.queue import get_queue_client

    # Override dependencies or setup test-specific configurations here if needed

    redis_mock: RedisMock = RedisMock(ping_response=True)
    async def override_get_queue_client():
        # Return a RedisMock instance for testing
        return redis_mock

    app.dependency_overrides[get_queue_client] = override_get_queue_client

    try:
        yield app, redis_mock
    finally:
        app.dependency_overrides.clear()

@pytest_asyncio.fixture
async def client_test(app_test: Tuple[FastAPI, RedisMock]):
    app, queue_client = app_test
    # Async client for testing FastAPI app
    async with AsyncClient(base_url="http://testserver", transport=ASGITransport(app=app)) as client:
        yield client, queue_client
