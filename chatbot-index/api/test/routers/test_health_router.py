import pytest

from httpx import AsyncClient

from src.routers.health import router as health_router

@pytest.mark.asyncio
async def test_health_check(client_test: AsyncClient):
    response = await client_test.get(url=health_router.prefix)

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "Chatbot Index API",
    }