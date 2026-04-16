import pytest

from httpx import AsyncClient, Response
from fastapi import FastAPI

from src.modules.queries.controller import router as query_router, get_query_service

from test.modules.queries.mocks import (
    get_query_service_get_queries_200_mock,
    get_query_service_get_queries_404_mock,
    get_query_service_create_query_201_mock,
    get_query_service_create_query_404_mock,
)


@pytest.mark.asyncio
async def test_get_queries_200(
    app_test: FastAPI,
    client_test: AsyncClient,
):
    app_test.dependency_overrides[get_query_service] = (
        get_query_service_get_queries_200_mock
    )

    response: Response = await client_test.get(
        url=f"{query_router.prefix}/123e4567-e89b-12d3-a456-426614174000",
        headers={"X-User-Id": "123e4567-e89b-12d3-a456-426614174000"},
    )

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_queries_404(
    app_test: FastAPI,
    client_test: AsyncClient,
):
    app_test.dependency_overrides[get_query_service] = (
        get_query_service_get_queries_404_mock
    )

    response: Response = await client_test.get(
        url=f"{query_router.prefix}/123e4567-e89b-12d3-a456-426614174000",
        headers={"X-User-Id": "123e4567-e89b-12d3-a456-426614174000"},
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_create_query_201(
    app_test: FastAPI,
    client_test: AsyncClient,
):
    app_test.dependency_overrides[get_query_service] = (
        get_query_service_create_query_201_mock
    )

    response: Response = await client_test.post(
        url=f"{query_router.prefix}/123e4567-e89b-12d3-a456-426614174000",
        headers={"X-User-Id": "123e4567-e89b-12d3-a456-426614174000"},
        json={"question": "What is the capital of France?"},
    )

    assert response.status_code == 201


@pytest.mark.asyncio
async def test_create_query_404(
    app_test: FastAPI,
    client_test: AsyncClient,
):
    app_test.dependency_overrides[get_query_service] = (
        get_query_service_create_query_404_mock
    )

    response: Response = await client_test.post(
        url=f"{query_router.prefix}/123e4567-e89b-12d3-a456-426614174000",
        headers={"X-User-Id": "123e4567-e89b-12d3-a456-426614174000"},
        json={"question": "What is the capital of France?"},
    )

    assert response.status_code == 404
