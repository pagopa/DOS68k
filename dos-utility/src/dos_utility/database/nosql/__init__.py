from contextlib import asynccontextmanager
from typing import AsyncGenerator
from .env import NoSQLProvider, NoSQLSettings, get_nosql_settings

from .interface import NoSQLInterface
from .models import KeyCondition, ConditionOperator, QueryResult, ScanResult
from .dynamodb import get_dynamodb_nosql


__all__ = [
    "get_nosql_client",
    "get_nosql_client_ctx",
    "NoSQLInterface",
    "KeyCondition",
    "ConditionOperator",
    "QueryResult",
    "ScanResult",
]


@asynccontextmanager
async def get_nosql_client_ctx() -> AsyncGenerator[NoSQLInterface, None]:
    """Asynchronous context manager to get the appropriate NoSQL client based on configuration.

    Yields:
        AsyncGenerator[NoSQLInterface, None]: An instance of the appropriate NoSQL client.

    Examples:
        >>> async with get_nosql_client_ctx() as nosql_client:
        >>>     item = await nosql_client.get_item("users", {"user_id": "123"})
    """
    nosql_settings: NoSQLSettings = get_nosql_settings()

    if nosql_settings.NOSQL_PROVIDER is NoSQLProvider.DYNAMODB:
        nosql: NoSQLInterface = get_dynamodb_nosql()

    async with nosql as nosql_client:
        yield nosql_client


# FastAPI dependency
async def get_nosql_client() -> AsyncGenerator[NoSQLInterface, None]:
    """FastAPI dependency to get the appropriate NoSQL client based on configuration.

    Yields:
        AsyncGenerator[NoSQLInterface, None]: An instance of the appropriate NoSQL client.

    Examples:
        >>> @app.get("/items")
        >>> async def get_items(nosql_client: Annotated[NoSQLInterface, Depends(get_nosql_client)]):
        >>>     item = await nosql_client.get_item("users", {"user_id": "123"})
    """
    async with get_nosql_client_ctx() as nosql_client:
        yield nosql_client
