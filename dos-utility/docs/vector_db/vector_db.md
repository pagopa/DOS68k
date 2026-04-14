# Table of Contents

* [dos\_utility.vector\_db](#dos_utility.vector_db)
  * [get\_vector\_db\_instance](#dos_utility.vector_db.get_vector_db_instance)
  * [get\_vector\_db\_ctx](#dos_utility.vector_db.get_vector_db_ctx)
  * [get\_vector\_db](#dos_utility.vector_db.get_vector_db)

<a id="dos_utility.vector_db"></a>

# dos\_utility.vector\_db

<a id="dos_utility.vector_db.get_vector_db_instance"></a>

#### get\_vector\_db\_instance

```python
def get_vector_db_instance(index_name: Optional[str] = None) -> VectorDBInterface
```

Return a VectorDB instance directly, without a context manager.

Intended for use with LlamaIndex (`VectorStoreIndex.from_vector_store`) where
the lifecycle is not request-scoped. The client is initialised at construction
time; no explicit connection step is required before calling async methods.

**Arguments**:

- `index_name` _Optional[str]_ - Pre-set index name required by the LlamaIndex `aquery` method.
    Pass `None` to create an instance for plain method calls where the index is specified per-call.

**Returns**:

- `VectorDBInterface` - The vector database instance.

**Examples**:

  >>> from dos_utility.vector_db import get_vector_db_instance
  >>> vdb = get_vector_db_instance(index_name="my_index")
  >>> # Use with LlamaIndex
  >>> index = VectorStoreIndex.from_vector_store(vector_store=vdb, embed_model=...)

<a id="dos_utility.vector_db.get_vector_db_ctx"></a>

#### get\_vector\_db\_ctx

```python
@asynccontextmanager
async def get_vector_db_ctx(index_name: Optional[str] = None) -> AsyncGenerator[VectorDBInterface, None]
```

Context manager to get the appropriate VectorDB implementation based on settings.

**Arguments**:

- `index_name` _Optional[str]_ - Optional index name to pre-set on the instance. When omitted,
    each method call must supply its own `index_name` argument.

**Yields**:

  AsyncGenerator[VectorDBInterface, None]: An asynchronous generator yielding the VectorDBInterface implementation

**Examples**:

  >>> async with get_vector_db_ctx() as vector_db:
  >>>     await vector_db.create_index(index_name="my_index", vector_dim=128)

<a id="dos_utility.vector_db.get_vector_db"></a>

#### get\_vector\_db

```python
async def get_vector_db(index_name: Optional[str] = None) -> AsyncGenerator[VectorDBInterface, None]
```

FastAPI dependency to get the appropriate VectorDB implementation based on settings.

**Arguments**:

- `index_name` _Optional[str]_ - Optional index name to pre-set on the instance.

**Yields**:

  AsyncGenerator[VectorDBInterface, None]: An asynchronous generator yielding the VectorDBInterface implementation

**Examples**:

  >>> @app.post("/create_index")
  >>> async def create_index(vector_db: Annotated[VectorDBInterface, Depends(get_vector_db)]):
  >>>     await vector_db.create_index(index_name="my_index", vector_dim=128)
