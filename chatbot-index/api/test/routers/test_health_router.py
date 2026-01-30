import pytest

from typing import Tuple
from httpx import AsyncClient, Response

from src.routers.health import router as health_router
from src.routers import health

from test.mocks import QueueMock, StorageMock

@pytest.mark.asyncio
async def test_health_check(client_test: Tuple[AsyncClient, QueueMock, StorageMock]):
    client, _, _ = client_test
    response: Response = await client.get(url=health_router.prefix)

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "Chatbot Index API",
    }

@pytest.mark.asyncio
async def test_health_check_queue_connected(client_test: Tuple[AsyncClient, QueueMock, StorageMock]):
    client, _, _ = client_test

    response: Response = await client.get(url=f"{health_router.prefix}/queue")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "Chatbot Index API",
        "queue": "connected",
    }

@pytest.mark.asyncio
async def test_health_check_queue_disconnected(client_test: Tuple[AsyncClient, QueueMock, StorageMock]):
    client, queue_client, _ = client_test

    # Simulate disconnected queue by setting ping_response to False
    queue_client.healthy = False

    response: Response = await client.get(url=f"{health_router.prefix}/queue")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "Chatbot Index API",
        "queue": "NOT connected",
    }

@pytest.mark.asyncio
async def test_health_check_storage_connected(
        client_test: Tuple[AsyncClient, QueueMock, StorageMock],
        monkeypatch: pytest.MonkeyPatch,
    ):
    monkeypatch.setattr(health, "StorageInterface", StorageMock)
    client, _, _ = client_test

    response: Response = await client.get(url=f"{health_router.prefix}/storage")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "Chatbot Index API",
        "storage": "connected",
    }

@pytest.mark.asyncio
async def test_health_check_storage_disconnected(
        client_test: Tuple[AsyncClient, QueueMock, StorageMock],
        monkeypatch: pytest.MonkeyPatch,
    ):
    monkeypatch.setattr(health, "StorageInterface", StorageMock)

    client, _, storage_client = client_test
    storage_client.healthy = False

    response: Response = await client.get(url=f"{health_router.prefix}/storage")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "Chatbot Index API",
        "storage": "NOT connected",
    }
