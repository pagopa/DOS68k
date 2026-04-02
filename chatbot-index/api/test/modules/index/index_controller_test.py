import pytest

from typing import Tuple
from fastapi import FastAPI
from httpx import AsyncClient, Response

from src.modules.index.controller import router as index_router
from src.modules.index.service import get_index_service
from src.modules.auth import get_user_id

from test.mocks import QueueMock, StorageMock, VectorDBMock
from test.modules.index.mocks import (
    MOCK_USER_ID,
    get_index_service_create_201_mock,
    get_index_service_create_409_mock,
    get_index_service_delete_204_mock,
    get_index_service_delete_404_mock,
    get_index_service_get_indexes_mock,
    get_index_service_get_indexes_empty_mock,
)


HEADERS = {"x-user-id": MOCK_USER_ID}


@pytest.mark.asyncio
async def test_create_index_201(client_test: Tuple[AsyncClient, QueueMock, StorageMock, VectorDBMock]):
    client, _, _, _ = client_test

    client_test_app: FastAPI = client._transport.app
    client_test_app.dependency_overrides[get_index_service] = get_index_service_create_201_mock

    response: Response = await client.post(url=f"{index_router.prefix}/my-index", headers=HEADERS)

    assert response.status_code == 201
    data = response.json()
    assert data["index_id"] == "my-index"
    assert data["userId"] == MOCK_USER_ID
    assert "createdAt" in data


@pytest.mark.asyncio
async def test_create_index_409(client_test: Tuple[AsyncClient, QueueMock, StorageMock, VectorDBMock]):
    client, _, _, _ = client_test

    client_test_app: FastAPI = client._transport.app
    client_test_app.dependency_overrides[get_index_service] = get_index_service_create_409_mock

    response: Response = await client.post(url=f"{index_router.prefix}/existing-index", headers=HEADERS)

    assert response.status_code == 409
    assert "already exists" in response.json()["detail"]


@pytest.mark.asyncio
async def test_delete_index_200(client_test: Tuple[AsyncClient, QueueMock, StorageMock, VectorDBMock]):
    client, _, _, _ = client_test

    client_test_app: FastAPI = client._transport.app
    client_test_app.dependency_overrides[get_index_service] = get_index_service_delete_204_mock

    response: Response = await client.delete(url=f"{index_router.prefix}/my-index", headers=HEADERS)

    assert response.status_code == 200
    assert "deleted successfully" in response.json()["message"]


@pytest.mark.asyncio
async def test_delete_index_404(client_test: Tuple[AsyncClient, QueueMock, StorageMock, VectorDBMock]):
    client, _, _, _ = client_test

    client_test_app: FastAPI = client._transport.app
    client_test_app.dependency_overrides[get_index_service] = get_index_service_delete_404_mock

    response: Response = await client.delete(url=f"{index_router.prefix}/nonexistent", headers=HEADERS)

    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


@pytest.mark.asyncio
async def test_get_indexes(client_test: Tuple[AsyncClient, QueueMock, StorageMock, VectorDBMock]):
    client, _, _, _ = client_test

    client_test_app: FastAPI = client._transport.app
    client_test_app.dependency_overrides[get_index_service] = get_index_service_get_indexes_mock

    response: Response = await client.get(url=f"{index_router.prefix}/all", headers=HEADERS)

    assert response.status_code == 200
    assert response.json() == ["index-1", "index-2"]


@pytest.mark.asyncio
async def test_get_indexes_empty(client_test: Tuple[AsyncClient, QueueMock, StorageMock, VectorDBMock]):
    client, _, _, _ = client_test

    client_test_app: FastAPI = client._transport.app
    client_test_app.dependency_overrides[get_index_service] = get_index_service_get_indexes_empty_mock

    response: Response = await client.get(url=f"{index_router.prefix}/all", headers=HEADERS)

    assert response.status_code == 200
    assert response.json() == []
