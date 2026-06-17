import pytest

from typing import Tuple
from httpx import AsyncClient, Response

from src.modules.evaluate.controller import (
    router as evaluate_router,
    get_evaluation_service,
)
from src.main import app

from test.mocks import QueueMock
from test.modules.evaluate.mocks import (
    get_evaluation_service_simple_feedback_201_mock,
    get_evaluation_service_simple_feedback_404_mock,
    get_evaluation_service_evaluate_201_mock,
    get_evaluation_service_evaluate_404_mock,
    get_evaluation_service_evaluate_all_201_mock,
    MOCK_SESSION_ID,
    MOCK_QUERY_ID,
    MOCK_USER_ID,
)


USER_HEADERS = {"X-User-Id": MOCK_USER_ID, "X-User-Role": "user"}
ADMIN_HEADERS = {"X-User-Id": MOCK_USER_ID, "X-User-Role": "admin"}


# ---------------------------------------------------------------------------
# POST /evaluate/simple-feedback/{session_id}/{query_id}
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_simple_feedback_201(client_test: Tuple[AsyncClient, QueueMock]):
    client, _ = client_test
    app.dependency_overrides[get_evaluation_service] = (
        get_evaluation_service_simple_feedback_201_mock
    )

    response: Response = await client.post(
        url=f"{evaluate_router.prefix}/simple-feedback/{MOCK_SESSION_ID}/{MOCK_QUERY_ID}",
        headers=USER_HEADERS,
        data={"feedback": "1"},
    )

    assert response.status_code == 201


@pytest.mark.asyncio
async def test_simple_feedback_404(client_test: Tuple[AsyncClient, QueueMock]):
    client, _ = client_test
    app.dependency_overrides[get_evaluation_service] = (
        get_evaluation_service_simple_feedback_404_mock
    )

    response: Response = await client.post(
        url=f"{evaluate_router.prefix}/simple-feedback/{MOCK_SESSION_ID}/{MOCK_QUERY_ID}",
        headers=USER_HEADERS,
        data={"feedback": "-1"},
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_simple_feedback_422_invalid_feedback_value(
    client_test: Tuple[AsyncClient, QueueMock],
):
    client, _ = client_test
    app.dependency_overrides[get_evaluation_service] = (
        get_evaluation_service_simple_feedback_201_mock
    )

    response: Response = await client.post(
        url=f"{evaluate_router.prefix}/simple-feedback/{MOCK_SESSION_ID}/{MOCK_QUERY_ID}",
        headers=USER_HEADERS,
        data={"feedback": "5"},
    )

    assert response.status_code == 422


# ---------------------------------------------------------------------------
# POST /evaluate/{session_id}/{query_id}
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_evaluate_201(client_test: Tuple[AsyncClient, QueueMock]):
    client, _ = client_test
    app.dependency_overrides[get_evaluation_service] = (
        get_evaluation_service_evaluate_201_mock
    )

    response: Response = await client.post(
        url=f"{evaluate_router.prefix}/{MOCK_SESSION_ID}/{MOCK_QUERY_ID}",
        headers=ADMIN_HEADERS,
    )

    assert response.status_code == 201


@pytest.mark.asyncio
async def test_evaluate_404(client_test: Tuple[AsyncClient, QueueMock]):
    client, _ = client_test
    app.dependency_overrides[get_evaluation_service] = (
        get_evaluation_service_evaluate_404_mock
    )

    response: Response = await client.post(
        url=f"{evaluate_router.prefix}/{MOCK_SESSION_ID}/{MOCK_QUERY_ID}",
        headers=ADMIN_HEADERS,
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_evaluate_403_non_admin(client_test: Tuple[AsyncClient, QueueMock]):
    client, _ = client_test
    app.dependency_overrides[get_evaluation_service] = (
        get_evaluation_service_evaluate_201_mock
    )

    response: Response = await client.post(
        url=f"{evaluate_router.prefix}/{MOCK_SESSION_ID}/{MOCK_QUERY_ID}",
        headers=USER_HEADERS,
    )

    assert response.status_code == 403


# ---------------------------------------------------------------------------
# POST /evaluate/all/{session_id}
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_evaluate_all_201(client_test: Tuple[AsyncClient, QueueMock]):
    client, _ = client_test
    app.dependency_overrides[get_evaluation_service] = (
        get_evaluation_service_evaluate_all_201_mock
    )

    response: Response = await client.post(
        url=f"{evaluate_router.prefix}/all/{MOCK_SESSION_ID}",
        headers=ADMIN_HEADERS,
    )

    assert response.status_code == 201


@pytest.mark.asyncio
async def test_evaluate_all_403_non_admin(client_test: Tuple[AsyncClient, QueueMock]):
    client, _ = client_test
    app.dependency_overrides[get_evaluation_service] = (
        get_evaluation_service_evaluate_all_201_mock
    )

    response: Response = await client.post(
        url=f"{evaluate_router.prefix}/all/{MOCK_SESSION_ID}",
        headers=USER_HEADERS,
    )

    assert response.status_code == 403
