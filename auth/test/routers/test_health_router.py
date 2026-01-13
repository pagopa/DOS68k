import pytest

from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check(client_test: AsyncClient):
    response = await client_test.get(url="/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "Auth Service",
    }