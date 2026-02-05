# Table of Contents

* [dos\_utility.vector\_db](#dos_utility.vector_db)
  * [get\_vector\_db\_ctx](#dos_utility.vector_db.get_vector_db_ctx)
  * [get\_vector\_db](#dos_utility.vector_db.get_vector_db)

<a id="dos_utility.vector_db"></a>

# dos\_utility.vector\_db

<a id="dos_utility.vector_db.get_vector_db_ctx"></a>

#### get\_vector\_db\_ctx

```python
@asynccontextmanager
async def get_vector_db_ctx() -> AsyncGenerator[VectorDBInterface, None]
```

Context manager to get the appropriate VectorDB implementation based on settings.

**Yields**:

  AsyncGenerator[VectorDBInterface, None]: An asynchronous generator yielding the VectorDBInterface implementation
  

**Examples**:

  >>> async with get_vector_db_ctx() as vector_db:
  >>>     await vector_db.create_index(index_name="my_index", vector_dim=128)

<a id="dos_utility.vector_db.get_vector_db"></a>

#### get\_vector\_db

```python
async def get_vector_db() -> AsyncGenerator[VectorDBInterface, None]
```

FastAPI dependency to get the appropriate VectorDB implementation based on settings.

**Yields**:

  AsyncGenerator[VectorDBInterface, None]: An asynchronous generator yielding the VectorDBInterface implementation
  

**Examples**:

  >>> @app.post("/create_index")
  >>> async def create_index(vector_db: Annotated[VectorDBInterface, Depends(get_vector_db)]):
  >>>     await vector_db.create_index(index_name="my_index", vector_dim=128)

