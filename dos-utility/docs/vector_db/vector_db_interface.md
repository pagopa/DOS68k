# Table of Contents

* [dos\_utility.vector\_db.interface](#dos_utility.vector_db.interface)
  * [ObjectData](#dos_utility.vector_db.interface.ObjectData)
  * [SemanticSearchResult](#dos_utility.vector_db.interface.SemanticSearchResult)
  * [VectorDBInterface](#dos_utility.vector_db.interface.VectorDBInterface)
    * [\_\_aenter\_\_](#dos_utility.vector_db.interface.VectorDBInterface.__aenter__)
    * [\_\_aexit\_\_](#dos_utility.vector_db.interface.VectorDBInterface.__aexit__)
    * [create\_index](#dos_utility.vector_db.interface.VectorDBInterface.create_index)
    * [delete\_index](#dos_utility.vector_db.interface.VectorDBInterface.delete_index)
    * [get\_indexes](#dos_utility.vector_db.interface.VectorDBInterface.get_indexes)
    * [put\_objects](#dos_utility.vector_db.interface.VectorDBInterface.put_objects)
    * [delete\_objects](#dos_utility.vector_db.interface.VectorDBInterface.delete_objects)
    * [semantic\_search](#dos_utility.vector_db.interface.VectorDBInterface.semantic_search)

<a id="dos_utility.vector_db.interface"></a>

# dos\_utility.vector\_db.interface

<a id="dos_utility.vector_db.interface.ObjectData"></a>

## ObjectData Objects

```python
class ObjectData(BaseModel)
```

Represents a single object to be stored in the vector database. Each object corresponds to a chunk of text from a file, along with its embedding vector.

<a id="dos_utility.vector_db.interface.SemanticSearchResult"></a>

## SemanticSearchResult Objects

```python
class SemanticSearchResult(BaseModel)
```

Represents a single result from a semantic search query. Each result corresponds to a chunk of text from a file, along with its similarity score to the query embedding.

<a id="dos_utility.vector_db.interface.VectorDBInterface"></a>

## VectorDBInterface Objects

```python
class VectorDBInterface(ABC)
```

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
The index will have this static structure:

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

- `data` _List[ObjectData]_ - A list of ObjectData to insert.
- `index_name` _str_ - The name of the index to insert the objects into.
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
    score_threshold: Annotated[PositiveFloat,
                               Field(ge=0.0, le=1.0)]
) -> List[SemanticSearchResult]
```

Perform a semantic search in the vector database.

**Arguments**:

- `index_name` _str_ - The name of the index to search in.
- `embedding_query` _List[float]_ - The embedding vector to search for. Make sure its dimension matches the index dimension.
- `max_results` _PositiveInt_ - The maximum number of results to return.
- `score_threshold` _PositiveFloat_ - The minimum similarity score (between 0 and 1) for a result to be included in the results list.
  

**Returns**:

- `List[SemanticSearchResult]` - A list of SemanticSearchResult objects representing the search results.
  

**Examples**:

  >>> vector_db = MyVectorDBImplementation()
  >>> async with vector_db as vdb:
  >>>     query_embedding: List[float] = [0.1, 0.2, 0.3, ...]  # Ensure the embedding dimension matches the index
  >>>     results: List[SemanticSearchResult] = await vdb.semantic_search(
  >>>         index_name="my_index",
  >>>         embedding_query=query_embedding,
  >>>         max_results=10,
  >>>         score_threshold=0.5,
  >>>     )

