import pytest
import pytest_asyncio
import asyncio
import os

from typing import Tuple
from fastapi import FastAPI
from httpx import AsyncClient, ASGITransport

from test.mocks import QueueMock, StorageMock


@pytest.fixture(scope="function")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture
async def app_test():
    from src.main import app
    from dos_utility.queue import get_queue_client
    from dos_utility.storage import get_storage

    # Override dependencies or setup test-specific configurations here if needed

    queue_mock: QueueMock = QueueMock()
    async def override_get_queue_client():
        yield queue_mock

    storage_mock: StorageMock = StorageMock()
    def override_get_storage():
        yield storage_mock

    app.dependency_overrides[get_queue_client] = override_get_queue_client
    app.dependency_overrides[get_storage] = override_get_storage

    try:
        yield app, queue_mock, storage_mock
    finally:
        app.dependency_overrides.clear()

@pytest_asyncio.fixture
async def client_test(app_test: Tuple[FastAPI, QueueMock, StorageMock]):
    app, queue_client, storage_client = app_test

    # Async client for testing FastAPI app
    async with AsyncClient(base_url="http://testserver", transport=ASGITransport(app=app)) as client:
        yield client, queue_client, storage_client