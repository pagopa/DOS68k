# Table of Contents

* [dos\_utility.database.nosql](#dos_utility.database.nosql)
  * [get\_nosql\_client\_ctx](#dos_utility.database.nosql.get_nosql_client_ctx)
  * [get\_nosql\_client](#dos_utility.database.nosql.get_nosql_client)

<a id="dos_utility.database.nosql"></a>

# dos\_utility.database.nosql

<a id="dos_utility.database.nosql.get_nosql_client_ctx"></a>

#### get\_nosql\_client\_ctx

```python
@asynccontextmanager
async def get_nosql_client_ctx() -> AsyncGenerator[NoSQLInterface, None]
```

Asynchronous context manager to get the appropriate NoSQL client based on configuration.

**Yields**:

  AsyncGenerator[NoSQLInterface, None]: An instance of the appropriate NoSQL client.
  

**Examples**:

  >>> async with get_nosql_client_ctx() as nosql_client:
  >>>     item = await nosql_client.get_item("users", {"user_id": "123"})

<a id="dos_utility.database.nosql.get_nosql_client"></a>

#### get\_nosql\_client

```python
async def get_nosql_client() -> AsyncGenerator[NoSQLInterface, None]
```

FastAPI dependency to get the appropriate NoSQL client based on configuration.

**Yields**:

  AsyncGenerator[NoSQLInterface, None]: An instance of the appropriate NoSQL client.
  

**Examples**:

  >>> @app.get("/items")
  >>> async def get_items(nosql_client: Annotated[NoSQLInterface, Depends(get_nosql_client)]):
  >>>     item = await nosql_client.get_item("users", {"user_id": "123"})

