import pytest
from httpx import AsyncClient
from src.routers.jwt_check import router as jwt_router

@pytest.mark.asyncio
auth_header = "Bearer dummy.jwt.token"

async def test_jwt_check_unauthorized(client_test: AsyncClient):
    response = await client_test.get(jwt_router.prefix + "/jwt-check")
    assert response.status_code == 422  # Missing header

async def test_jwt_check_invalid_token(client_test: AsyncClient):
    response = await client_test.get(jwt_router.prefix + "/jwt-check", headers={"Authorization": auth_header})
    assert response.status_code in (401, 503)  # Invalid token or JWKS unavailable
