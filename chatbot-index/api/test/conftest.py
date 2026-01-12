import pytest
import pytest_asyncio

from fastapi import FastAPI
from httpx import AsyncClient, ASGITransport


@pytest_asyncio.fixture
async def app_test() -> FastAPI:
    from src.main import app

    # Override dependencies or setup test-specific configurations here if needed

    try:
        yield app
    finally:
        app.dependency_overrides.clear()

@pytest_asyncio.fixture
async def client_test(app_test: FastAPI):
    # Async client for testing FastAPI app
    async with AsyncClient(base_url="http://testserver", transport=ASGITransport(app=app_test)) as client:
        yield client
