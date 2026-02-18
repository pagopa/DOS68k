import pytest

from typing import AsyncGenerator, Callable

from dos_utility.database import nosql
from dos_utility.database.nosql import NoSQLInterface, get_nosql_client, get_nosql_settings, get_nosql_client_ctx

from test.database.nosql.mocks import get_nosql_settings_dynamodb_mock, get_dynamodb_nosql_mock



@pytest.mark.asyncio
async def test_nosql_db_interface_not_instantiable():
    with pytest.raises(expected_exception=TypeError):
        async with NoSQLInterface():
            pass

@pytest.mark.asyncio
@pytest.mark.parametrize(
    "get_nosql_settings_mock, func_to_mock, get_nosql_mock",
    [
        (get_nosql_settings_dynamodb_mock, "get_dynamodb_nosql", get_dynamodb_nosql_mock),
    ],
)
async def test_get_nosql_db_client(monkeypatch: pytest.MonkeyPatch, get_nosql_settings_mock: Callable, func_to_mock: str, get_nosql_mock: Callable):
    get_nosql_settings.cache_clear()

    monkeypatch.setattr(nosql, "get_nosql_settings", get_nosql_settings_mock)
    monkeypatch.setattr(nosql, func_to_mock, get_nosql_mock)

    nosql_gen: AsyncGenerator[NoSQLInterface, None] = get_nosql_client()
    client: NoSQLInterface = await nosql_gen.__anext__()

    assert isinstance(client, NoSQLInterface)

@pytest.mark.asyncio
@pytest.mark.parametrize(
    "get_nosql_settings_mock, func_to_mock, get_nosql_mock",
    [
        (get_nosql_settings_dynamodb_mock, "get_dynamodb_nosql", get_dynamodb_nosql_mock),
    ],
)
async def test_get_nosql_client_ctx(monkeypatch: pytest.MonkeyPatch, get_nosql_settings_mock: Callable, func_to_mock: str, get_nosql_mock: Callable):
    get_nosql_settings.cache_clear()

    monkeypatch.setattr(nosql, "get_nosql_settings", get_nosql_settings_mock)
    monkeypatch.setattr(nosql, func_to_mock, get_nosql_mock)

    async with get_nosql_client_ctx() as client:
        print(type(client))
        assert isinstance(client, NoSQLInterface)
