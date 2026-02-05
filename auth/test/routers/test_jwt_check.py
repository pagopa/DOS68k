import pytest
from httpx import AsyncClient
from src.routers.jwt_check import router as jwt_router


@pytest.mark.asyncio
async def test_jwt_check_unauthorized(client_test: AsyncClient):
    """Test JWT check without Authorization header should return 422 (validation error)."""
    response = await client_test.get(jwt_router.prefix + "/jwt-check")
    assert response.status_code == 422  # Missing header


@pytest.mark.asyncio
async def test_jwt_check_invalid_token(client_test: AsyncClient):
    """Test JWT check with invalid token should return 401 or 500."""
    auth_header = "Bearer dummy.jwt.token"
    response = await client_test.get(jwt_router.prefix + "/jwt-check", headers={"Authorization": auth_header})
    assert response.status_code in (401, 500)  # Invalid token or JWKS unavailable
