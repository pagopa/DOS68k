import asyncio
from abc import abstractmethod
from typing import Self, List, Annotated, Optional, Any
from pydantic import BaseModel, Field, PositiveFloat, PositiveInt
from llama_index.core.vector_stores.types import BasePydanticVectorStore, VectorStoreQuery, VectorStoreQueryResult, MetadataFilters



class ObjectData(BaseModel):
    """Represents a single object to be stored in the vector database. Each object corresponds to a chunk of text from a file, along with its embedding vector.
    """
    filename: Annotated[str, Field(description="The name of the file the object comes from.")]
    chunk_id: Annotated[int, Field(description="The chunk ID within the file. If the file is not chunked set it to 0.")]
    content: Annotated[str, Field(description="The content of the chunk.")]
    vector: Annotated[List[float], Field(description="The embedding vector of the content. Make sure its dimension matches the vector DB index dimension.")]

class SearchResult(BaseModel):
    """Represents a single result from a vector DB search (semantic or filter-based).
    """
    id: Annotated[str, Field(description="Unique identifier of the document")]
    filename: Annotated[str, Field(description="Name of the file containing the document")]
    chunk_id: Annotated[int, Field(description="Chunk identifier within the document")]
    content: Annotated[str, Field(description="Content of the document chunk")]
    score: Annotated[Optional[float], Field(description="Similarity score between 0 and 1. None for filter-only results.")]



class VectorDBInterface(BasePydanticVectorStore):
    stores_text: bool = True

    @abstractmethod
    def model_post_init(self: Self, __context: Any) -> None:
        """Initialize private attributes (database clients, settings, etc.).

        Use this instead of __init__: because this class ultimately inherits from
        Pydantic's BaseModel (via BasePydanticVectorStore), __init__ is owned by
        Pydantic and must not be overridden. model_post_init runs after Pydantic
        has finished its own initialization, with all fields already validated and set.
        """
        ...

    @property
    @abstractmethod
    def client(self: Self) -> Any:
        """Get the underlying database client."""
        ...

    def add(self: Self, nodes: Any, **kwargs: Any) -> List[str]:
        raise NotImplementedError

    def delete(self: Self, ref_doc_id: str, **delete_kwargs: Any) -> None:
        raise NotImplementedError

    def query(self: Self, query: VectorStoreQuery, **kwargs: Any) -> VectorStoreQueryResult:
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            # Inside an already-running event loop (e.g. FastAPI) — create a new
            # thread to avoid "cannot run nested event loop" errors.
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                return pool.submit(asyncio.run, self.aquery(query, **kwargs)).result()
        else:
            return asyncio.run(self.aquery(query, **kwargs))

    @abstractmethod
    async def __aenter__(self: Self) -> Self:
        """Enter the asynchronous context manager.

        Examples:
            >>> vector_db = MyVectorDBImplementation()
            >>> async with vector_db as vdb:
            >>>     # Use vdb to interact with the vector database
        """
        ...

    @abstractmethod
    async def __aexit__(self: Self, exc_type, exc_value, traceback) -> None:
        """Exit the asynchronous context manager.

        Examples:
            >>> vector_db = MyVectorDBImplementation()
            >>> async with vector_db as vdb:
            >>>     # Use vdb to interact with the vector database
        """
        ...

    @abstractmethod
    async def create_index(self: Self, index_name: str, vector_dim: int) -> None:
        """Create a new index in the vector database.
        The index will have this static structure:

        Args:
            index_name (str): The name of the index to create.
            vector_dim (int): The dimension of the embedding vectors.

        Raises:
            IndexCreationException: If index creation fails.

        Examples:
            >>> vector_db = MyVectorDBImplementation()
            >>> async with vector_db as vdb:
            >>>     try:
            >>>         await vdb.create_index(index_name="my_index", vector_dim=128)
            >>>     except IndexCreationException as e:
            >>>         ... # handle the exception
        """
        ...

    @abstractmethod
    async def delete_index(self: Self, index_name: str) -> None:
        """Delete an index from the vector database.

        Args:
            index_name (str): The name of the index to delete.

        Raises:
            IndexDeletionException: If index deletion fails.

        Examples:
            >>> vector_db = MyVectorDBImplementation()
            >>> async with vector_db as vdb:
            >>>     try:
            >>>         await vdb.delete_index(index_name="my_index")
            >>>     except IndexDeletionException as e:
            >>>         ... # handle the exception
        """
        ...

    @abstractmethod
    async def get_indexes(self: Self) -> List[str]:
        """Get all indexes from the vector database, as a list of strings.

        Returns:
            List[str]: A list of index names.

        Examples:
            >>> vector_db = MyVectorDBImplementation()
            >>> async with vector_db as vdb:
            >>>     indexes: List[str] = await vdb.get_indexes()
        """
        ...

    @abstractmethod
    async def put_objects(self: Self, index_name: str, data: List[ObjectData], custom_keys: Optional[List[str]]=None) -> List[str]:
        """Put objects into the vector database.
        If custom keys are provided and they match keys of already existing objects, those objects will be overwritten.

        Args:
            data (List[ObjectData]): A list of ObjectData to insert.
            index_name (str): The name of the index to insert the objects into.
            custom_keys (Optional[List[str]]): An optional list of keys to use for the objects. If provided, the objects will be inserted with these keys instead of auto-generated ones.

        Returns:
            List[str]: A list of inserted object IDs.

        Raises:
            PutObjectsException: If putting objects fails.

        Examples:
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
        """
        ...

    @abstractmethod
    async def delete_objects(self: Self, index_name: str, ids: List[str]) -> None:
        """Delete objects from the vector database.

        Args:
            index_name (str): The name of the index to delete the objects from.
            ids (List[str]): A list of object IDs to delete.

        Raises:
            DeleteObjectsException: If deleting objects fails.

        Examples:
            >>> vector_db = MyVectorDBImplementation()
            >>> async with vector_db as vdb:
            >>>     ids_to_delete: List[str] = ["id1", "id2", "id3"]
            >>>     try:
            >>>         await vdb.delete_objects(index_name="my_index", ids=ids_to_delete)
            >>>     except DeleteObjectsException as e:
            >>>         ... # handle the exception
        """
        ...

    @abstractmethod
    async def semantic_search(
            self: Self,
            index_name: str,
            embedding_query: List[float],
            max_results: PositiveInt,
            score_threshold: Annotated[PositiveFloat, Field(ge=0.0, le=1.0)],
            filters: Optional[MetadataFilters] = None,
        ) -> List[SearchResult]:
        """Perform a semantic search in the vector database.

        Args:
            index_name (str): The name of the index to search in.
            embedding_query (List[float]): The embedding vector to search for. Make sure its dimension matches the index dimension.
            max_results (PositiveInt): The maximum number of results to return.
            score_threshold (PositiveFloat): The minimum similarity score (between 0 and 1) for a result to be included in the results list.
            filters (Optional[MetadataFilters]): Optional metadata filters to apply alongside the vector search.

        Returns:
            List[SearchResult]: A list of SearchResult objects representing the search results.

        Examples:
            >>> vector_db = MyVectorDBImplementation()
            >>> async with vector_db as vdb:
            >>>     query_embedding: List[float] = [0.1, 0.2, 0.3, ...]  # Ensure the embedding dimension matches the index
            >>>     results: List[SearchResult] = await vdb.semantic_search(
            >>>         index_name="my_index",
            >>>         embedding_query=query_embedding,
            >>>         max_results=10,
            >>>         score_threshold=0.5,
            >>>     )
        """
        ...

    @abstractmethod
    async def filter_search(
            self: Self,
            index_name: str,
            filters: MetadataFilters,
            max_results: PositiveInt,
        ) -> List[SearchResult]:
        """Perform a metadata filter search in the vector database, without a query embedding.

        Args:
            index_name (str): The name of the index to search in.
            filters (MetadataFilters): The metadata filters to apply.
            max_results (PositiveInt): The maximum number of results to return.

        Returns:
            List[SearchResult]: A list of SearchResult objects. score is None for all results.

        Examples:
            >>> from llama_index.core.vector_stores.types import MetadataFilters, MetadataFilter
            >>> vector_db = MyVectorDBImplementation()
            >>> async with vector_db as vdb:
            >>>     results: List[SearchResult] = await vdb.filter_search(
            >>>         index_name="my_index",
            >>>         filters=MetadataFilters(filters=[MetadataFilter(key="filename", value="doc.pdf")]),
            >>>         max_results=10,
            >>>     )
        """
        ...

    @abstractmethod
    async def aquery(self: Self, query: VectorStoreQuery, **kwargs: Any) -> VectorStoreQueryResult:
        """LlamaIndex integration point. Routes to semantic_search or filter_search
        based on whether query.query_embedding is set, then converts the results to
        the VectorStoreQueryResult format expected by LlamaIndex.
        """
        ...
