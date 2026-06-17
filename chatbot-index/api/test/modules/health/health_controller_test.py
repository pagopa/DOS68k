import pytest

from typing import Tuple
from httpx import AsyncClient, Response

from src.modules.health.controller import router as health_router

from test.mocks import QueueMock, StorageMock, VectorDBMock


@pytest.mark.asyncio
async def test_health_check(
    client_test: Tuple[AsyncClient, QueueMock, StorageMock, VectorDBMock],
):
    client, _, _, _ = client_test
    response: Response = await client.get(url=health_router.prefix)

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "Chatbot Index API",
    }


@pytest.mark.asyncio
async def test_health_check_queue_connected(
    client_test: Tuple[AsyncClient, QueueMock, StorageMock, VectorDBMock],
):
    client, _, _, _ = client_test

    response: Response = await client.get(url=f"{health_router.prefix}/queue")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "Chatbot Index API",
        "queue": "connected",
    }


@pytest.mark.asyncio
async def test_health_check_queue_disconnected(
    client_test: Tuple[AsyncClient, QueueMock, StorageMock, VectorDBMock],
):
    client, queue_client, _, _ = client_test
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
    client_test: Tuple[AsyncClient, QueueMock, StorageMock, VectorDBMock],
):
    client, _, _, _ = client_test

    response: Response = await client.get(url=f"{health_router.prefix}/storage")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "Chatbot Index API",
        "storage": "connected",
    }


@pytest.mark.asyncio
async def test_health_check_storage_disconnected(
    client_test: Tuple[AsyncClient, QueueMock, StorageMock, VectorDBMock],
):
    client, _, storage_client, _ = client_test
    storage_client.healthy = False

    response: Response = await client.get(url=f"{health_router.prefix}/storage")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "Chatbot Index API",
        "storage": "NOT connected",
    }


@pytest.mark.asyncio
async def test_health_check_vdb_connected(
    client_test: Tuple[AsyncClient, QueueMock, StorageMock, VectorDBMock],
):
    client, _, _, _ = client_test

    response: Response = await client.get(url=f"{health_router.prefix}/vdb")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "Chatbot Index API",
        "vector_db": "connected",
    }


@pytest.mark.asyncio
async def test_health_check_vdb_disconnected(
    client_test: Tuple[AsyncClient, QueueMock, StorageMock, VectorDBMock],
):
    client, _, _, vdb_client = client_test
    vdb_client.healthy = False

    response: Response = await client.get(url=f"{health_router.prefix}/vdb")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "Chatbot Index API",
        "vector_db": "NOT connected",
    }
