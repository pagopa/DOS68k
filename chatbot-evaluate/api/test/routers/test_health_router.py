import pytest

from typing import Tuple
from httpx import AsyncClient

from src.routers.health import router as health_router

from test.mocks import QueueMock

@pytest.mark.asyncio
async def test_health_check(client_test: Tuple[AsyncClient, QueueMock]):
    client, _ = client_test
    response = await client.get(url=health_router.prefix)

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "Chatbot Evaluate API",
    }

@pytest.mark.asyncio
async def test_health_check_db(client_test: Tuple[AsyncClient, QueueMock]):
    client, _ = client_test
    response = await client.get(url=f"{health_router.prefix}/db")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "Chatbot Evaluate API",
        "database": "connected",
    }

@pytest.mark.asyncio
async def test_health_check_queue_connected(client_test: Tuple[AsyncClient, QueueMock]):
    client, _ = client_test

    response = await client.get(url=f"{health_router.prefix}/queue")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "Chatbot Evaluate API",
        "queue": "connected",
    }

@pytest.mark.asyncio
async def test_health_check_queue_disconnected(client_test: Tuple[AsyncClient, QueueMock]):
    client, queue_client = client_test

    # Simulate disconnected queue by setting ping_response to False
    queue_client.healthy = False

    response = await client.get(url=f"{health_router.prefix}/queue")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "Chatbot Evaluate API",
        "queue": "NOT connected",
    }
