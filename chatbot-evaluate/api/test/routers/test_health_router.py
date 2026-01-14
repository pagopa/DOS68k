import pytest

from typing import Tuple
from httpx import AsyncClient

from src.routers.health import router as health_router

from test.mocks import RedisMock

@pytest.mark.asyncio
async def test_health_check(client_test: Tuple[AsyncClient, RedisMock]):
    client, _ = client_test
    response = await client.get(url=health_router.prefix)

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "Chatbot Evaluate API",
    }

@pytest.mark.asyncio
async def test_health_check_db(client_test: Tuple[AsyncClient, RedisMock]):
    client, _ = client_test
    response = await client.get(url=f"{health_router.prefix}/db")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "Chatbot Evaluate API",
        "database": "connected",
    }

@pytest.mark.asyncio
async def test_health_check_queue_connected(client_test: Tuple[AsyncClient, RedisMock]):
    client, _ = client_test

    response = await client.get(url=f"{health_router.prefix}/queue")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "Chatbot Evaluate API",
        "queue": "connected",
    }

@pytest.mark.asyncio
async def test_health_check_queue_disconnected(client_test: Tuple[AsyncClient, RedisMock]):
    client, queue_client = client_test

    # Simulate disconnected queue by setting ping_response to False
    queue_client.ping_response = False

    response = await client.get(url=f"{health_router.prefix}/queue")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "Chatbot Evaluate API",
        "queue": "not connected",
    }

@pytest.mark.asyncio
async def test_health_check_queue_exception(client_test: Tuple[AsyncClient, RedisMock]):
    client, queue_client = client_test

    # Simulate exception during ping
    queue_client.ping_response = "exception"

    response = await client.get(url=f"{health_router.prefix}/queue")

    assert response.status_code == 200
    assert response.json() == {
        "status": "error",
        "service": "Chatbot Evaluate API",
        "queue": "connection error: Mocked connection error",
    }