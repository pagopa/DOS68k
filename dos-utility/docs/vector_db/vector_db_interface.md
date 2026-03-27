# Table of Contents

* [dos\_utility.vector\_db.interface](#dos_utility.vector_db.interface)
  * [ObjectData](#dos_utility.vector_db.interface.ObjectData)
  * [SearchResult](#dos_utility.vector_db.interface.SearchResult)
  * [VectorDBInterface](#dos_utility.vector_db.interface.VectorDBInterface)
    * [model\_post\_init](#dos_utility.vector_db.interface.VectorDBInterface.model_post_init)
    * [client](#dos_utility.vector_db.interface.VectorDBInterface.client)
    * [\_\_aenter\_\_](#dos_utility.vector_db.interface.VectorDBInterface.__aenter__)
    * [\_\_aexit\_\_](#dos_utility.vector_db.interface.VectorDBInterface.__aexit__)
    * [create\_index](#dos_utility.vector_db.interface.VectorDBInterface.create_index)
    * [delete\_index](#dos_utility.vector_db.interface.VectorDBInterface.delete_index)
    * [get\_indexes](#dos_utility.vector_db.interface.VectorDBInterface.get_indexes)
    * [put\_objects](#dos_utility.vector_db.interface.VectorDBInterface.put_objects)
    * [delete\_objects](#dos_utility.vector_db.interface.VectorDBInterface.delete_objects)
    * [semantic\_search](#dos_utility.vector_db.interface.VectorDBInterface.semantic_search)
    * [filter\_search](#dos_utility.vector_db.interface.VectorDBInterface.filter_search)
    * [aquery](#dos_utility.vector_db.interface.VectorDBInterface.aquery)

<a id="dos_utility.vector_db.interface"></a>

# dos\_utility.vector\_db.interface

<a id="dos_utility.vector_db.interface.ObjectData"></a>

## ObjectData Objects

```python
class ObjectData(BaseModel)
```

Represents a single object to be stored in the vector database. Each object corresponds to a chunk of text from a file, along with its embedding vector.

**Attributes**:

- `filename` _str_ - The name of the file the object comes from.
- `chunk_id` _int_ - The chunk ID within the file. If the file is not chunked set it to 0.
- `content` _str_ - The content of the chunk.
- `embedding` _List[float]_ - The embedding vector of the content. Make sure its dimension matches the vector DB index dimension.

<a id="dos_utility.vector_db.interface.SearchResult"></a>

## SearchResult Objects

```python
class SearchResult(BaseModel)
```

Represents a single result from a vector DB search (semantic or filter-based).

**Attributes**:

- `id` _str_ - Unique identifier of the document.
- `filename` _str_ - Name of the file containing the document.
- `chunk_id` _int_ - Chunk identifier within the document.
- `content` _str_ - Content of the document chunk.
- `score` _Optional[float]_ - Similarity score between 0 and 1. `None` for filter-only results.

<a id="dos_utility.vector_db.interface.VectorDBInterface"></a>

## VectorDBInterface Objects

```python
class VectorDBInterface(BasePydanticVectorStore)
```

Abstract interface for vector database operations. Extends LlamaIndex's `BasePydanticVectorStore` to enable seamless LlamaIndex integration via the `aquery` method.

Since this class inherits from Pydantic's `BaseModel` (via `BasePydanticVectorStore`), implementations must not override `__init__`. Use `model_post_init` instead.

<a id="dos_utility.vector_db.interface.VectorDBInterface.model_post_init"></a>

#### model\_post\_init

```python
@abstractmethod
def model_post_init(__context: Any) -> None
```

Initialize private attributes (database clients, settings, etc.).

Use this instead of `__init__`: because this class ultimately inherits from
Pydantic's `BaseModel`, `__init__` is owned by Pydantic and must not be overridden.
`model_post_init` runs after Pydantic has finished its own initialization, with all
fields already validated and set.

<a id="dos_utility.vector_db.interface.VectorDBInterface.client"></a>

#### client

```python
@property
@abstractmethod
def client() -> Any
```

Get the underlying database client (e.g. `AsyncQdrantClient`, `redis.asyncio.Redis`).

<a id="dos_utility.vector_db.interface.VectorDBInterface.__aenter__"></a>

#### \_\_aenter\_\_

```python
@abstractmethod
async def __aenter__() -> Self
```

Enter the asynchronous context manager.

**Examples**:

  >>> vector_db = MyVectorDBImplementation()
  >>> async with vector_db as vdb:
  >>>     # Use vdb to interact with the vector database

<a id="dos_utility.vector_db.interface.VectorDBInterface.__aexit__"></a>

#### \_\_aexit\_\_

```python
@abstractmethod
async def __aexit__(exc_type, exc_value, traceback) -> None
```

Exit the asynchronous context manager.

**Examples**:

  >>> vector_db = MyVectorDBImplementation()
  >>> async with vector_db as vdb:
  >>>     # Use vdb to interact with the vector database

<a id="dos_utility.vector_db.interface.VectorDBInterface.create_index"></a>

#### create\_index

```python
@abstractmethod
async def create_index(index_name: str, vector_dim: int) -> None
```

Create a new index in the vector database.

**Arguments**:

- `index_name` _str_ - The name of the index to create.
- `vector_dim` _int_ - The dimension of the embedding vectors.

**Raises**:

- `IndexCreationException` - If index creation fails.

**Examples**:

  >>> vector_db = MyVectorDBImplementation()
  >>> async with vector_db as vdb:
  >>>     try:
  >>>         await vdb.create_index(index_name="my_index", vector_dim=128)
  >>>     except IndexCreationException as e:
  >>>         ... # handle the exception

<a id="dos_utility.vector_db.interface.VectorDBInterface.delete_index"></a>

#### delete\_index

```python
@abstractmethod
async def delete_index(index_name: str) -> None
```

Delete an index from the vector database.

**Arguments**:

- `index_name` _str_ - The name of the index to delete.

**Raises**:

- `IndexDeletionException` - If index deletion fails.

**Examples**:

  >>> vector_db = MyVectorDBImplementation()
  >>> async with vector_db as vdb:
  >>>     try:
  >>>         await vdb.delete_index(index_name="my_index")
  >>>     except IndexDeletionException as e:
  >>>         ... # handle the exception

<a id="dos_utility.vector_db.interface.VectorDBInterface.get_indexes"></a>

#### get\_indexes

```python
@abstractmethod
async def get_indexes() -> List[str]
```

Get all indexes from the vector database, as a list of strings.

**Returns**:

- `List[str]` - A list of index names.

**Examples**:

  >>> vector_db = MyVectorDBImplementation()
  >>> async with vector_db as vdb:
  >>>     indexes: List[str] = await vdb.get_indexes()

<a id="dos_utility.vector_db.interface.VectorDBInterface.put_objects"></a>

#### put\_objects

```python
@abstractmethod
async def put_objects(index_name: str,
                      data: List[ObjectData],
                      custom_keys: Optional[List[str]] = None) -> List[str]
```

Put objects into the vector database.
If custom keys are provided and they match keys of already existing objects, those objects will be overwritten.

**Arguments**:

- `index_name` _str_ - The name of the index to insert the objects into.
- `data` _List[ObjectData]_ - A list of ObjectData to insert.
- `custom_keys` _Optional[List[str]]_ - An optional list of keys to use for the objects. If provided, the objects will be inserted with these keys instead of auto-generated ones.

**Returns**:

- `List[str]` - A list of inserted object IDs.

**Raises**:

- `PutObjectsException` - If putting objects fails.

**Examples**:

  >>> vector_db = MyVectorDBImplementation()
  >>> async with vector_db as vdb:
  >>>     my_data: List[ObjectData] = [
  >>>         ObjectData(
  >>>             filename="example.txt",
  >>>             chunk_id=0,
  >>>             content="This is an example chunk of text.",
  >>>             embedding=[0.1, 0.2, 0.3, ...],  # Ensure the embedding dimension matches the index
  >>>         ),
  >>>         # Add more ObjectData instances as needed
  >>>     ]
  >>>     try:
  >>>         ids: List[str] = await vdb.put_objects(index_name="my_index", data=my_data)
  >>>     except PutObjectsException as e:
  >>>         ... # handle the exception

<a id="dos_utility.vector_db.interface.VectorDBInterface.delete_objects"></a>

#### delete\_objects

```python
@abstractmethod
async def delete_objects(index_name: str, ids: List[str]) -> None
```

Delete objects from the vector database.

**Arguments**:

- `index_name` _str_ - The name of the index to delete the objects from.
- `ids` _List[str]_ - A list of object IDs to delete.

**Raises**:

- `DeleteObjectsException` - If deleting objects fails.

**Examples**:

  >>> vector_db = MyVectorDBImplementation()
  >>> async with vector_db as vdb:
  >>>     ids_to_delete: List[str] = ["id1", "id2", "id3"]
  >>>     try:
  >>>         await vdb.delete_objects(index_name="my_index", ids=ids_to_delete)
  >>>     except DeleteObjectsException as e:
  >>>         ... # handle the exception

<a id="dos_utility.vector_db.interface.VectorDBInterface.semantic_search"></a>

#### semantic\_search

```python
@abstractmethod
async def semantic_search(
    index_name: str, embedding_query: List[float], max_results: PositiveInt,
    score_threshold: Annotated[PositiveFloat, Field(ge=0.0, le=1.0)],
    filters: Optional[MetadataFilters] = None
) -> List[SearchResult]
```

Perform a semantic search in the vector database.

**Arguments**:

- `index_name` _str_ - The name of the index to search in.
- `embedding_query` _List[float]_ - The embedding vector to search for. Make sure its dimension matches the index dimension.
- `max_results` _PositiveInt_ - The maximum number of results to return.
- `score_threshold` _PositiveFloat_ - The minimum similarity score (between 0 and 1) for a result to be included in the results list.
- `filters` _Optional[MetadataFilters]_ - Optional metadata filters (from LlamaIndex) to apply alongside the vector search.

**Returns**:

- `List[SearchResult]` - A list of SearchResult objects representing the search results.

**Examples**:

  >>> vector_db = MyVectorDBImplementation()
  >>> async with vector_db as vdb:
  >>>     query_embedding: List[float] = [0.1, 0.2, 0.3, ...]  # Ensure the embedding dimension matches the index
  >>>     results: List[SearchResult] = await vdb.semantic_search(
  >>>         index_name="my_index",
  >>>         embedding_query=query_embedding,
  >>>         max_results=10,
  >>>         score_threshold=0.5,
  >>>     )

  With metadata filters:

  >>> from llama_index.core.vector_stores.types import MetadataFilters, MetadataFilter
  >>> results = await vdb.semantic_search(
  >>>     index_name="my_index",
  >>>     embedding_query=query_embedding,
  >>>     max_results=10,
  >>>     score_threshold=0.5,
  >>>     filters=MetadataFilters(filters=[MetadataFilter(key="filename", value="doc.pdf")]),
  >>> )

<a id="dos_utility.vector_db.interface.VectorDBInterface.filter_search"></a>

#### filter\_search

```python
@abstractmethod
async def filter_search(
    index_name: str, filters: MetadataFilters, max_results: PositiveInt
) -> List[SearchResult]
```

Perform a metadata filter search in the vector database, without a query embedding.

**Arguments**:

- `index_name` _str_ - The name of the index to search in.
- `filters` _MetadataFilters_ - The metadata filters to apply (from LlamaIndex).
- `max_results` _PositiveInt_ - The maximum number of results to return.

**Returns**:

- `List[SearchResult]` - A list of SearchResult objects. `score` is `None` for all results.

**Examples**:

  >>> from llama_index.core.vector_stores.types import MetadataFilters, MetadataFilter
  >>> vector_db = MyVectorDBImplementation()
  >>> async with vector_db as vdb:
  >>>     results: List[SearchResult] = await vdb.filter_search(
  >>>         index_name="my_index",
  >>>         filters=MetadataFilters(filters=[MetadataFilter(key="filename", value="doc.pdf")]),
  >>>         max_results=10,
  >>>     )

<a id="dos_utility.vector_db.interface.VectorDBInterface.aquery"></a>

#### aquery

```python
@abstractmethod
async def aquery(query: VectorStoreQuery, **kwargs: Any) -> VectorStoreQueryResult
```

LlamaIndex integration point. Routes to `semantic_search` or `filter_search`
based on whether `query.query_embedding` is set, then converts the results to
the `VectorStoreQueryResult` format expected by LlamaIndex.

Requires `index_name` to be set at construction time (via `get_vector_db_instance(index_name="...")`).

**Arguments**:

- `query` _VectorStoreQuery_ - The LlamaIndex query object.

**Returns**:

- `VectorStoreQueryResult` - The query results in LlamaIndex format.

**Raises**:

- `ValueError` - If `index_name` was not set at construction time, or if neither `query_embedding` nor `filters` is provided.

**Examples**:

  >>> from dos_utility.vector_db import get_vector_db_instance
  >>> from llama_index.core.vector_stores.types import VectorStoreQuery
  >>> vdb = get_vector_db_instance(index_name="my_index")
  >>> result = await vdb.aquery(VectorStoreQuery(query_embedding=[0.1, 0.2, ...], similarity_top_k=5))
