import uuid

try:
    uuid.uuid7  # Python 3.14+
except AttributeError:
    from uuid6 import uuid7 as _uuid7

    uuid.uuid7 = _uuid7

import pytest
import pytest_asyncio
import asyncio

from fastapi import FastAPI
from httpx import AsyncClient, ASGITransport

from test.mocks import override_get_nosql_client


@pytest.fixture(scope="function")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def app_test():
    from src.main import app
    from dos_utility.database.nosql import get_nosql_client

    # Override dependencies or setup test-specific configurations here if needed

    app.dependency_overrides[get_nosql_client] = override_get_nosql_client

    try:
        yield app
    finally:
        app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def client_test(app_test: FastAPI):
    # Async client for testing FastAPI app
    async with AsyncClient(
        base_url="http://testserver", transport=ASGITransport(app=app_test)
    ) as client:
        yield client
