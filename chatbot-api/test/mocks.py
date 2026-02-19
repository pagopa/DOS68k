from typing import Self, Dict, Any, Optional, List

from dos_utility.database.nosql import NoSQLInterface, KeyCondition, QueryResult, ScanResult


class MockNoSQLDatabase(NoSQLInterface):
    def __init__(self: Self):
        self._data: Dict[str, Any] = {} # To be used for storing data in-memory for testing purposes

    async def __aenter__(self: Self) -> Self:
        return self

    async def __aexit__(self: Self, exc_type, exc_val, exc_tb) -> None:
        pass

    async def is_healthy(self: Self) -> bool:
        return True

    async def put_item(self: Self, table_name: str, item: Dict[str, Any]) -> None: ...

    async def get_item(self: Self, table_name: str, key: Dict[str, Any]) -> Optional[Dict[str, Any]]: ...

    async def delete_item(self: Self, table_name: str, key: Dict[str, Any]) -> None: ...

    async def update_item(
        self: Self,
        table_name: str,
        key: Dict[str, Any],
        fields_to_update: Dict[str, Any],
    ) -> None: ...

    async def query(
        self: Self,
        table_name: str,
        key_conditions: List[KeyCondition],
        index_name: Optional[str] = None,
        sort_ascending: bool = True,
        limit: Optional[int] = None,
        count_only: bool = False,
    ) -> QueryResult:
        ...

    async def scan(
        self: Self,
        table_name: str,
        limit: Optional[int] = None,
        start_key: Optional[Dict[str, Any]] = None,
    ) -> ScanResult:
        ...


def override_get_nosql_client() -> MockNoSQLDatabase:
    return MockNoSQLDatabase()