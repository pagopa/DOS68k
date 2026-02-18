# Table of Contents

* [dos\_utility.database.nosql.interface](#dos_utility.database.nosql.interface)
  * [NoSQLInterface](#dos_utility.database.nosql.interface.NoSQLInterface)
    * [\_\_aenter\_\_](#dos_utility.database.nosql.interface.NoSQLInterface.__aenter__)
    * [\_\_aexit\_\_](#dos_utility.database.nosql.interface.NoSQLInterface.__aexit__)
    * [is\_healthy](#dos_utility.database.nosql.interface.NoSQLInterface.is_healthy)
    * [put\_item](#dos_utility.database.nosql.interface.NoSQLInterface.put_item)
    * [get\_item](#dos_utility.database.nosql.interface.NoSQLInterface.get_item)
    * [delete\_item](#dos_utility.database.nosql.interface.NoSQLInterface.delete_item)
    * [update\_item](#dos_utility.database.nosql.interface.NoSQLInterface.update_item)
    * [query](#dos_utility.database.nosql.interface.NoSQLInterface.query)
    * [scan](#dos_utility.database.nosql.interface.NoSQLInterface.scan)

<a id="dos_utility.database.nosql.interface"></a>

# dos\_utility.database.nosql.interface

<a id="dos_utility.database.nosql.interface.NoSQLInterface"></a>

## NoSQLInterface Objects

```python
class NoSQLInterface(ABC)
```

<a id="dos_utility.database.nosql.interface.NoSQLInterface.__aenter__"></a>

#### \_\_aenter\_\_

```python
@abstractmethod
async def __aenter__() -> Self
```

Enter the asynchronous context manager.

**Returns**:

- `Self` - The instance of the NoSQL client.
  

**Examples**:

  >>> nosql = MyNoSQLImplementation()
  >>> async with nosql as client:
  >>>     # Use client to interact with the NoSQL database

<a id="dos_utility.database.nosql.interface.NoSQLInterface.__aexit__"></a>

#### \_\_aexit\_\_

```python
@abstractmethod
async def __aexit__(exc_type, exc_val, exc_tb) -> None
```

Exit the asynchronous context manager.

**Examples**:

  >>> nosql = MyNoSQLImplementation()
  >>> async with nosql as client:
  >>>     # Use client to interact with the NoSQL database

<a id="dos_utility.database.nosql.interface.NoSQLInterface.is_healthy"></a>

#### is\_healthy

```python
@abstractmethod
async def is_healthy() -> bool
```

Check if the NoSQL service is healthy/reachable.
If the implementation could raise an exception when not healthy, it should be caught and False returned.

**Returns**:

- `bool` - True if healthy, False otherwise.

<a id="dos_utility.database.nosql.interface.NoSQLInterface.put_item"></a>

#### put\_item

```python
@abstractmethod
async def put_item(table_name: str, item: Dict[str, Any]) -> None
```

Insert or replace a full document in the specified table.

**Arguments**:

- `table_name` _str_ - The name of the table.
- `item` _Dict[str, Any]_ - The document to insert or replace.
  

**Examples**:

  >>> await client.put_item("users", {"user_id": "123", "name": "Alice"})

<a id="dos_utility.database.nosql.interface.NoSQLInterface.get_item"></a>

#### get\_item

```python
@abstractmethod
async def get_item(table_name: str,
                   key: Dict[str, Any]) -> Optional[Dict[str, Any]]
```

Fetch a single item by primary key.

**Arguments**:

- `table_name` _str_ - The name of the table.
- `key` _Dict[str, Any]_ - The primary key of the item.
  

**Returns**:

  Optional[Dict[str, Any]]: The item if found, None otherwise.
  

**Examples**:

  >>> item = await client.get_item("users", {"user_id": "123"})

<a id="dos_utility.database.nosql.interface.NoSQLInterface.delete_item"></a>

#### delete\_item

```python
@abstractmethod
async def delete_item(table_name: str, key: Dict[str, Any]) -> None
```

Delete a single item by primary key.

**Arguments**:

- `table_name` _str_ - The name of the table.
- `key` _Dict[str, Any]_ - The primary key of the item to delete.
  

**Examples**:

  >>> await client.delete_item("users", {"user_id": "123"})

<a id="dos_utility.database.nosql.interface.NoSQLInterface.update_item"></a>

#### update\_item

```python
@abstractmethod
async def update_item(
        table_name: str, key: Dict[str, Any],
        fields_to_update: Dict[str, Any]) -> Optional[Dict[str, Any]]
```

Update specific fields of a document and return the updated document.

**Arguments**:

- `table_name` _str_ - The name of the table.
- `key` _Dict[str, Any]_ - The primary key of the item to update.
- `fields_to_update` _Dict[str, Any]_ - A dictionary of field names and their new values.
  

**Returns**:

  Optional[Dict[str, Any]]: The updated document, or None if the item was not found.
  

**Examples**:

  >>> updated = await client.update_item("users", {"user_id": "123"}, {"name": "Bob"})

<a id="dos_utility.database.nosql.interface.NoSQLInterface.query"></a>

#### query

```python
@abstractmethod
async def query(table_name: str,
                key_conditions: List[KeyCondition],
                index_name: Optional[str] = None,
                sort_ascending: bool = True,
                limit: Optional[int] = None,
                count_only: bool = False) -> QueryResult
```

Query items by key conditions.

**Arguments**:

- `table_name` _str_ - The name of the table.
- `key_conditions` _List[KeyCondition]_ - Conditions to filter items by key.
- `index_name` _Optional[str]_ - The name of the secondary index to query.
- `sort_ascending` _bool_ - Whether to sort results in ascending order.
- `limit` _Optional[int]_ - Maximum number of items to return.
- `count_only` _bool_ - If True, only return the count of matching items.
  

**Returns**:

- `QueryResult` - The query results containing items and count.
  

**Examples**:

  >>> from dos_utility.nosql.models import KeyCondition, ConditionOperator
  >>> result = await client.query(
  ...     "sessions",
  ...     [KeyCondition("user_id", ConditionOperator.EQ, "123")],
  ...     sort_ascending=False,
  ...     limit=10,
  ... )

<a id="dos_utility.database.nosql.interface.NoSQLInterface.scan"></a>

#### scan

```python
@abstractmethod
async def scan(table_name: str,
               limit: Optional[int] = None,
               start_key: Optional[Dict[str, Any]] = None) -> ScanResult
```

Perform a paginated full-table scan.

**Arguments**:

- `table_name` _str_ - The name of the table.
- `limit` _Optional[int]_ - Maximum number of items to return per page.
- `start_key` _Optional[Dict[str, Any]]_ - The key to start scanning from (for pagination).
  

**Returns**:

- `ScanResult` - The scan results containing items and the last evaluated key.
  

**Examples**:

  >>> result = await client.scan("queries", limit=100)
  >>> while result.last_evaluated_key:
  ...     result = await client.scan("queries", limit=100, start_key=result.last_evaluated_key)

