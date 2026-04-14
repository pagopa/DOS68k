import pytest
from httpx import AsyncClient

from src.modules.health.controller import router as health_router


@pytest.mark.asyncio
async def test_health_check(client_test: AsyncClient):
    """Health check endpoint returns 200 with service status."""
    response = await client_test.get(url=health_router.prefix)

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "Auth Service",
    }
