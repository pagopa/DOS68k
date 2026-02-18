from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Self

from dos_utility.database.nosql.env import NoSQLProvider
from dos_utility.database.nosql.interface import NoSQLInterface
from dos_utility.database.nosql.models import KeyCondition, QueryResult, ScanResult



class MockNoSQLClient(NoSQLInterface):
    async def __aenter__(self: Self) -> Self: return self

    async def __aexit__(self: Self, exc_type, exc_val, exc_tb) -> None: ...

    async def is_healthy(self: Self) -> bool: ...

    async def put_item(self: Self, table_name: str, item: Dict[str, Any]) -> None: ...

    async def get_item(self: Self, table_name: str, key: Dict[str, Any]) -> Optional[Dict[str, Any]]: ...

    async def delete_item(self: Self, table_name: str, key: Dict[str, Any]) -> None: ...

    async def update_item(
        self: Self,
        table_name: str,
        key: Dict[str, Any],
        fields_to_update: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]: ...

    async def query(
        self: Self,
        table_name: str,
        key_conditions: List[KeyCondition],
        index_name: Optional[str] = None,
        sort_ascending: bool = True,
        limit: Optional[int] = None,
        count_only: bool = False,
    ) -> QueryResult: ...

    async def scan(
        self: Self,
        table_name: str,
        limit: Optional[int] = None,
        start_key: Optional[Dict[str, Any]] = None,
    ) -> ScanResult: ...

class MockDynamoDBClient(MockNoSQLClient):
    pass

def get_dynamodb_nosql_mock() -> MockDynamoDBClient:
    return MockDynamoDBClient()

@dataclass
class NoSQLDBSettingsMock:
    NOSQL_PROVIDER: str

def get_nosql_settings_dynamodb_mock():
    return NoSQLDBSettingsMock(NOSQL_PROVIDER=NoSQLProvider.DYNAMODB)
