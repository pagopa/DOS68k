import pytest

from typing import Tuple
from fastapi import FastAPI
from httpx import AsyncClient, Response

from src.modules.document.controller import router as document_router
from src.modules.document.service import get_document_service
from src.modules.auth import get_user_id

from test.mocks import QueueMock, StorageMock, VectorDBMock
from test.modules.document.mocks import (
    MOCK_USER_ID,
    get_document_service_upload_202_mock,
    get_document_service_upload_404_mock,
    get_document_service_upload_415_mock,
    get_document_service_list_200_mock,
    get_document_service_list_empty_mock,
    get_document_service_list_404_mock,
    get_document_service_delete_200_mock,
    get_document_service_delete_404_mock,
)


HEADERS = {"x-user-id": MOCK_USER_ID}
INDEX_ID = "test-index"
DOCUMENT_NAME = "test.pdf"
BASE_URL = document_router.prefix.replace("{index_id}", INDEX_ID)


# ---------------------------------------------------------------------------
# POST /index/{index_id}/documents — upload
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_upload_document_202(client_test: Tuple[AsyncClient, QueueMock, StorageMock, VectorDBMock]):
    client, _, _, _ = client_test
    app: FastAPI = client._transport.app
    app.dependency_overrides[get_document_service] = get_document_service_upload_202_mock

    response: Response = await client.post(
        url=BASE_URL,
        headers=HEADERS,
        files={"file": (DOCUMENT_NAME, b"pdf content", "application/pdf")},
    )

    assert response.status_code == 202
    data = response.json()
    assert data["indexId"] == INDEX_ID
    assert data["documentName"] == DOCUMENT_NAME
    assert "uploaded successfully" in data["message"]


@pytest.mark.asyncio
async def test_upload_document_404_index_not_found(client_test: Tuple[AsyncClient, QueueMock, StorageMock, VectorDBMock]):
    client, _, _, _ = client_test
    app: FastAPI = client._transport.app
    app.dependency_overrides[get_document_service] = get_document_service_upload_404_mock

    response: Response = await client.post(
        url=BASE_URL,
        headers=HEADERS,
        files={"file": (DOCUMENT_NAME, b"pdf content", "application/pdf")},
    )

    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


@pytest.mark.asyncio
async def test_upload_document_415_unsupported_type(client_test: Tuple[AsyncClient, QueueMock, StorageMock, VectorDBMock]):
    client, _, _, _ = client_test
    app: FastAPI = client._transport.app
    app.dependency_overrides[get_document_service] = get_document_service_upload_415_mock

    response: Response = await client.post(
        url=BASE_URL,
        headers=HEADERS,
        files={"file": ("file.docx", b"docx content", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
    )

    assert response.status_code == 415


@pytest.mark.asyncio
async def test_upload_document_missing_auth_header(client_test: Tuple[AsyncClient, QueueMock, StorageMock, VectorDBMock]):
    client, _, _, _ = client_test
    app: FastAPI = client._transport.app
    app.dependency_overrides[get_document_service] = get_document_service_upload_202_mock

    response: Response = await client.post(
        url=BASE_URL,
        files={"file": (DOCUMENT_NAME, b"pdf content", "application/pdf")},
    )

    assert response.status_code == 422


# ---------------------------------------------------------------------------
# GET /index/{index_id}/documents — list
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_list_documents_200(client_test: Tuple[AsyncClient, QueueMock, StorageMock, VectorDBMock]):
    client, _, _, _ = client_test
    app: FastAPI = client._transport.app
    app.dependency_overrides[get_document_service] = get_document_service_list_200_mock

    response: Response = await client.get(url=BASE_URL, headers=HEADERS)

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2


@pytest.mark.asyncio
async def test_list_documents_200_empty(client_test: Tuple[AsyncClient, QueueMock, StorageMock, VectorDBMock]):
    client, _, _, _ = client_test
    app: FastAPI = client._transport.app
    app.dependency_overrides[get_document_service] = get_document_service_list_empty_mock

    response: Response = await client.get(url=BASE_URL, headers=HEADERS)

    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_list_documents_404_index_not_found(client_test: Tuple[AsyncClient, QueueMock, StorageMock, VectorDBMock]):
    client, _, _, _ = client_test
    app: FastAPI = client._transport.app
    app.dependency_overrides[get_document_service] = get_document_service_list_404_mock

    response: Response = await client.get(url=BASE_URL, headers=HEADERS)

    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


# ---------------------------------------------------------------------------
# DELETE /index/{index_id}/documents/{document_name} — delete
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_delete_document_200(client_test: Tuple[AsyncClient, QueueMock, StorageMock, VectorDBMock]):
    client, _, _, _ = client_test
    app: FastAPI = client._transport.app
    app.dependency_overrides[get_document_service] = get_document_service_delete_200_mock

    response: Response = await client.delete(
        url=f"{BASE_URL}/{DOCUMENT_NAME}", headers=HEADERS
    )

    assert response.status_code == 200
    data = response.json()
    assert DOCUMENT_NAME in data["message"]
    assert INDEX_ID in data["message"]


@pytest.mark.asyncio
async def test_delete_document_404_not_found(client_test: Tuple[AsyncClient, QueueMock, StorageMock, VectorDBMock]):
    client, _, _, _ = client_test
    app: FastAPI = client._transport.app
    app.dependency_overrides[get_document_service] = get_document_service_delete_404_mock

    response: Response = await client.delete(
        url=f"{BASE_URL}/{DOCUMENT_NAME}", headers=HEADERS
    )

    assert response.status_code == 404
    assert "not found" in response.json()["detail"]
