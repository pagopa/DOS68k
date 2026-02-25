import pytest

from httpx import AsyncClient, Response
from fastapi import FastAPI

from src.modules.sessions.controller import get_session_service, router as sessions_router

from test.modules.sessions.mocks import (
    get_session_service_create_session_mock,
    get_session_service_delete_session_204_mock,
    get_session_service_delete_session_404_mock,
    get_session_service_get_session_200_mock,
    get_session_service_get_session_404_mock,
    get_session_service_get_sessions_mock,
)


@pytest.mark.asyncio
async def test_get_sessions(app_test: FastAPI, client_test: AsyncClient):
    app_test.dependency_overrides[get_session_service] = get_session_service_get_sessions_mock

    response: Response = await client_test.get(
        url=f"{sessions_router.prefix}/all",
        headers={"X-User-Id": "123e4567-e89b-12d3-a456-426614174000"},
    )

    assert response.status_code == 200

@pytest.mark.asyncio
async def test_get_session_200(app_test: FastAPI, client_test: AsyncClient):
    app_test.dependency_overrides[get_session_service] = get_session_service_get_session_200_mock

    response: Response = await client_test.get(
        url=f"{sessions_router.prefix}/123e4567-e89b-12d3-a456-426614174000",
        headers={"X-User-Id": "123e4567-e89b-12d3-a456-426614174000"},
    )

    assert response.status_code == 200

@pytest.mark.asyncio
async def test_get_session_404(app_test: FastAPI, client_test: AsyncClient):
    app_test.dependency_overrides[get_session_service] = get_session_service_get_session_404_mock

    response: Response = await client_test.get(
        url=f"{sessions_router.prefix}/123e4567-e89b-12d3-a456-426614174000",
        headers={"X-User-Id": "123e4567-e89b-12d3-a456-426614174000"},
    )

    assert response.status_code == 404

@pytest.mark.asyncio
async def test_create_session(app_test: FastAPI, client_test: AsyncClient):
    app_test.dependency_overrides[get_session_service] = get_session_service_create_session_mock

    response: Response = await client_test.post(
        url=f"{sessions_router.prefix}",
        headers={"X-User-Id": "123e4567-e89b-12d3-a456-426614174000"},
        json={"title": "New Session", "is_temporary": False},
    )

    assert response.status_code == 201

@pytest.mark.asyncio
async def test_delete_session_204(app_test: FastAPI, client_test: AsyncClient):
    app_test.dependency_overrides[get_session_service] = get_session_service_delete_session_204_mock

    response: Response = await client_test.delete(
        url=f"{sessions_router.prefix}/123e4567-e89b-12d3-a456-426614174000",
        headers={"X-User-Id": "123e4567-e89b-12d3-a456-426614174000"},
    )

    assert response.status_code == 204

@pytest.mark.asyncio
async def test_delete_session_404(app_test: FastAPI, client_test: AsyncClient):
    app_test.dependency_overrides[get_session_service] = get_session_service_delete_session_404_mock

    response: Response = await client_test.delete(
        url=f"{sessions_router.prefix}/123e4567-e89b-12d3-a456-426614174000",
        headers={"X-User-Id": "123e4567-e89b-12d3-a456-426614174000"},
    )

    assert response.status_code == 404