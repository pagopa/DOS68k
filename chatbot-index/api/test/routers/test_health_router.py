import pytest

from typing import Tuple
from httpx import AsyncClient, Response

from src.routers.health import router as health_router
from src.routers import health

from test.mocks import RedisMock, AWSS3ConnectedMock, AWSS3ExceptionMock

@pytest.mark.asyncio
async def test_health_check(client_test: Tuple[AsyncClient, RedisMock]):
    client, _ = client_test
    response: Response = await client.get(url=health_router.prefix)

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "Chatbot Index API",
    }

@pytest.mark.asyncio
async def test_health_check_queue_connected(client_test: Tuple[AsyncClient, RedisMock]):
    client, _ = client_test

    response: Response = await client.get(url=f"{health_router.prefix}/queue")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "Chatbot Index API",
        "queue": "connected",
    }

@pytest.mark.asyncio
async def test_health_check_queue_disconnected(client_test: Tuple[AsyncClient, RedisMock]):
    client, queue_client = client_test

    # Simulate disconnected queue by setting ping_response to False
    queue_client.ping_response = False

    response: Response = await client.get(url=f"{health_router.prefix}/queue")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "Chatbot Index API",
        "queue": "not connected",
    }

@pytest.mark.asyncio
async def test_health_check_queue_exception(client_test: Tuple[AsyncClient, RedisMock]):
    client, queue_client = client_test

    # Simulate exception during ping
    queue_client.ping_response = "exception"

    response: Response = await client.get(url=f"{health_router.prefix}/queue")

    assert response.status_code == 200
    assert response.json() == {
        "status": "error",
        "service": "Chatbot Index API",
        "queue": "connection error: Mocked queue connection error",
    }

@pytest.mark.asyncio
async def test_health_check_storage_connected(
        client_test: Tuple[AsyncClient, RedisMock],
        monkeypatch: pytest.MonkeyPatch,
    ):
    monkeypatch.setattr(health, "AWSS3", AWSS3ConnectedMock)
    client, _ = client_test

    response: Response = await client.get(url=f"{health_router.prefix}/storage")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "Chatbot Index API",
        "storage": "connected",
    }

@pytest.mark.asyncio
async def test_health_check_storage_exception(
        client_test: Tuple[AsyncClient, RedisMock],
        monkeypatch: pytest.MonkeyPatch,
    ):
    monkeypatch.setattr(health, "AWSS3", AWSS3ExceptionMock)

    client, _ = client_test

    response: Response = await client.get(url=f"{health_router.prefix}/storage")

    assert response.status_code == 200
    assert response.json() == {
        "status": "error",
        "service": "Chatbot Index API",
        "storage": "connection error: Mocked storage connection error",
    }
