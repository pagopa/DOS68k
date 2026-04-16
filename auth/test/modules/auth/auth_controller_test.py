import pytest
from httpx import AsyncClient, Response
from fastapi import FastAPI

from src.modules.auth.controller import router as auth_router, get_auth_service
from test.modules.auth.mocks import (
    get_auth_service_200_mock,
    get_auth_service_401_mock,
    get_auth_service_500_mock,
)


@pytest.mark.asyncio
async def test_jwt_check_200(app_test: FastAPI, client_test: AsyncClient):
    app_test.dependency_overrides[get_auth_service] = get_auth_service_200_mock

    response: Response = await client_test.get(
        url=f"{auth_router.prefix}/jwt-check",
        headers={"Authorization": "Bearer valid-token"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "payload" in data
    assert "sub" in data["payload"]


@pytest.mark.asyncio
async def test_jwt_check_401(app_test: FastAPI, client_test: AsyncClient):
    app_test.dependency_overrides[get_auth_service] = get_auth_service_401_mock

    response: Response = await client_test.get(
        url=f"{auth_router.prefix}/jwt-check",
        headers={"Authorization": "Bearer invalid-token"},
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_jwt_check_500(app_test: FastAPI, client_test: AsyncClient):
    app_test.dependency_overrides[get_auth_service] = get_auth_service_500_mock

    response: Response = await client_test.get(
        url=f"{auth_router.prefix}/jwt-check",
        headers={"Authorization": "Bearer valid-token"},
    )

    assert response.status_code == 500
