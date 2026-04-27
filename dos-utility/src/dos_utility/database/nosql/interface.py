from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Self

from .models import KeyCondition, QueryResult, ScanResult


class NoSQLInterface(ABC):
    @abstractmethod
    async def __aenter__(self: Self) -> Self:
        """Enter the asynchronous context manager.

        Returns:
            Self: The instance of the NoSQL client.

        Examples:
            >>> nosql = MyNoSQLImplementation()
            >>> async with nosql as client:
            >>>     # Use client to interact with the NoSQL database
        """
        ...

    @abstractmethod
    async def __aexit__(self: Self, exc_type, exc_val, exc_tb) -> None:
        """Exit the asynchronous context manager.

        Examples:
            >>> nosql = MyNoSQLImplementation()
            >>> async with nosql as client:
            >>>     # Use client to interact with the NoSQL database
        """
        ...

    @abstractmethod
    async def is_healthy(self: Self) -> bool:
        """Check if the NoSQL service is healthy/reachable.
        If the implementation could raise an exception when not healthy, it should be caught and False returned.

        Returns:
            bool: True if healthy, False otherwise.
        """
        ...

    @abstractmethod
    async def put_item(self: Self, table_name: str, item: Dict[str, Any]) -> None:
        """Insert or replace a full document in the specified table.

        Args:
            table_name (str): The name of the table.
            item (Dict[str, Any]): The document to insert or replace.

        Examples:
            >>> await client.put_item("users", {"user_id": "123", "name": "Alice"})
        """
        ...

    @abstractmethod
    async def get_item(
        self: Self, table_name: str, key: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Fetch a single item by primary key.

        Args:
            table_name (str): The name of the table.
            key (Dict[str, Any]): The primary key of the item.

        Returns:
            Optional[Dict[str, Any]]: The item if found, None otherwise.

        Examples:
            >>> item = await client.get_item("users", {"user_id": "123"})
        """
        ...

    @abstractmethod
    async def delete_item(self: Self, table_name: str, key: Dict[str, Any]) -> None:
        """Delete a single item by primary key.

        Args:
            table_name (str): The name of the table.
            key (Dict[str, Any]): The primary key of the item to delete.

        Examples:
            >>> await client.delete_item("users", {"user_id": "123"})
        """
        ...

    @abstractmethod
    async def update_item(
        self: Self,
        table_name: str,
        key: Dict[str, Any],
        fields_to_update: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        """Update specific fields of a document and return the updated document.

        Args:
            table_name (str): The name of the table.
            key (Dict[str, Any]): The primary key of the item to update.
            fields_to_update (Dict[str, Any]): A dictionary of field names and their new values.

        Returns:
            Optional[Dict[str, Any]]: The updated document, or None if the item was not found.

        Examples:
            >>> updated = await client.update_item("users", {"user_id": "123"}, {"name": "Bob"})
        """
        ...

    @abstractmethod
    async def query(
        self: Self,
        table_name: str,
        key_conditions: List[KeyCondition],
        index_name: Optional[str] = None,
        sort_ascending: bool = True,
        limit: Optional[int] = None,
        count_only: bool = False,
    ) -> QueryResult:
        """Query items by key conditions.

        Args:
            table_name (str): The name of the table.
            key_conditions (List[KeyCondition]): Conditions to filter items by key.
            index_name (Optional[str]): The name of the secondary index to query.
            sort_ascending (bool): Whether to sort results in ascending order.
            limit (Optional[int]): Maximum number of items to return.
            count_only (bool): If True, only return the count of matching items.

        Returns:
            QueryResult: The query results containing items and count.

        Examples:
            >>> from dos_utility.nosql.models import KeyCondition, ConditionOperator
            >>> result = await client.query(
            ...     "sessions",
            ...     [KeyCondition("user_id", ConditionOperator.EQ, "123")],
            ...     sort_ascending=False,
            ...     limit=10,
            ... )
        """
        ...

    @abstractmethod
    async def scan(
        self: Self,
        table_name: str,
        limit: Optional[int] = None,
        start_key: Optional[Dict[str, Any]] = None,
    ) -> ScanResult:
        """Perform a paginated full-table scan.

        Args:
            table_name (str): The name of the table.
            limit (Optional[int]): Maximum number of items to return per page.
            start_key (Optional[Dict[str, Any]]): The key to start scanning from (for pagination).

        Returns:
            ScanResult: The scan results containing items and the last evaluated key.

        Examples:
            >>> result = await client.scan("queries", limit=100)
            >>> while result.last_evaluated_key:
            ...     result = await client.scan("queries", limit=100, start_key=result.last_evaluated_key)
        """
        ...
