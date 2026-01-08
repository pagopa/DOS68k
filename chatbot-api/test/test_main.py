import pytest


@pytest.mark.asyncio
async def test_health_check(client_test):
    response = await client_test.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}