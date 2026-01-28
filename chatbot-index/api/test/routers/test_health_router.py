import pytest

from typing import Tuple, Literal
from httpx import AsyncClient, Response

from src.routers.health import router as health_router
from src.routers import health

from test.mocks import QueueMock, AWSS3ConnectedMock, AWSS3ExceptionMock

@pytest.mark.asyncio
async def test_health_check(client_test: Tuple[AsyncClient, QueueMock]):
    client, _ = client_test
    response: Response = await client.get(url=health_router.prefix)

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "Chatbot Index API",
    }

@pytest.mark.asyncio
async def test_health_check_queue_connected(client_test: Tuple[AsyncClient, QueueMock]):
    client, _ = client_test

    response: Response = await client.get(url=f"{health_router.prefix}/queue")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "Chatbot Index API",
        "queue": "connected",
    }

@pytest.mark.asyncio
@pytest.mark.parametrize(
    "ping_response",
    [
        False,
        "exception",
    ],
)
async def test_health_check_queue_disconnected(client_test: Tuple[AsyncClient, QueueMock], ping_response: Literal[False, "exception"]):
    client, queue_client = client_test

    # Simulate disconnected queue by setting ping_response to False
    queue_client.ping_response = ping_response

    response: Response = await client.get(url=f"{health_router.prefix}/queue")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "Chatbot Index API",
        "queue": "NOT connected",
    }

@pytest.mark.asyncio
async def test_health_check_storage_connected(
        client_test: Tuple[AsyncClient, QueueMock],
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
        client_test: Tuple[AsyncClient, QueueMock],
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
