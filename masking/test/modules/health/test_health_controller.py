import pytest

from httpx import AsyncClient, Response


@pytest.mark.asyncio
async def test_health_check(client_test: AsyncClient) -> None:
    """GET /health returns 200 with service status."""
    response: Response = await client_test.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "Masking Service"}
