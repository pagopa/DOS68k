import pytest

from fastapi import FastAPI
from httpx import AsyncClient, Response

from src.modules.mask.service import get_mask_service

from test.modules.mask.mocks import MaskServiceMock


@pytest.mark.asyncio
async def test_mask_endpoint_success(app_test: FastAPI, client_test: AsyncClient) -> None:
    """POST /mask/ with valid body returns 200 and masked text."""
    mock_service: MaskServiceMock = MaskServiceMock()
    mock_service.mask_return_value = "masked output"

    app_test.dependency_overrides[get_mask_service] = lambda: mock_service

    response: Response = await client_test.post("/mask", json={"text": "my secret"})
    assert response.status_code == 200
    assert response.json() == "masked output"


@pytest.mark.asyncio
async def test_mask_endpoint_missing_body(app_test: FastAPI, client_test: AsyncClient) -> None:
    """POST /mask/ with no body returns 422."""
    mock_service: MaskServiceMock = MaskServiceMock()
    app_test.dependency_overrides[get_mask_service] = lambda: mock_service

    response: Response = await client_test.post("/mask")
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_mask_endpoint_empty_text(app_test: FastAPI, client_test: AsyncClient) -> None:
    """POST /mask/ with empty text returns 200 (empty string is valid)."""
    mock_service: MaskServiceMock = MaskServiceMock()
    mock_service.mask_return_value = ""

    app_test.dependency_overrides[get_mask_service] = lambda: mock_service

    response: Response = await client_test.post("/mask", json={"text": ""})
    assert response.status_code == 200
    assert response.json() == ""
