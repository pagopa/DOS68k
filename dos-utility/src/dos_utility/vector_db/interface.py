from abc import ABC, abstractmethod
from typing import Self, List, Annotated, Optional
from pydantic import BaseModel, Field, PositiveFloat, PositiveInt



class ObjectData(BaseModel):
    """Represents a single object to be stored in the vector database. Each object corresponds to a chunk of text from a file, along with its embedding vector.
    """
    filename: Annotated[str, Field(description="The name of the file the object comes from.")]
    chunk_id: Annotated[int, Field(description="The chunk ID within the file. If the file is not chunked set it to 0.")]
    content: Annotated[str, Field(description="The content of the chunk.")]
    embedding: Annotated[List[float], Field(description="The embedding vector of the content. Make sure its dimension matches the vector DB index dimension.")]

class SemanticSearchResult(BaseModel):
    """Represents a single result from a semantic search query. Each result corresponds to a chunk of text from a file, along with its similarity score to the query embedding.
    """
    id: Annotated[str, Field(description="Unique identifier of the document")]
    filename: Annotated[str, Field(description="Name of the file containing the document")]
    chunk_id: Annotated[int, Field(description="Chunk identifier within the document")]
    content: Annotated[str, Field(description="Content of the document chunk")]
    score: Annotated[float, Field(description="Similarity score between 0 and 1")]

class VectorDBInterface(ABC):
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

        Examples:
            >>> vector_db = MyVectorDBImplementation()
            >>> async with vector_db as vdb:
            >>>     await vdb.create_index(index_name="my_index", vector_dim=128)
        """
        ...

    @abstractmethod
    async def delete_index(self: Self, index_name: str) -> None:
        """Delete an index from the vector database.

        Args:
            index_name (str): The name of the index to delete.

        Examples:
            >>> vector_db = MyVectorDBImplementation()
            >>> async with vector_db as vdb:
            >>>     await vdb.delete_index(index_name="my_index")
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
    async def put_objects(self: Self, data: List[ObjectData], custom_keys: Optional[List[str]]=None) -> List[str]:
        """Put objects into the vector database.
        If custom keys are provided and they match keys of already existing objects, those objects will be overwritten.

        Args:
            data (List[ObjectData]): A list of ObjectData to insert.
            custom_keys (Optional[List[str]]): An optional list of keys to use for the objects. If provided, the objects will be inserted with these keys instead of auto-generated ones.

        Returns:
            List[str]: A list of inserted object IDs.

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
            >>>     ids: List[str] = await vdb.put_objects(data=my_data)
        """
        ...

    @abstractmethod
    async def delete_objects(self: Self, ids: List[str]) -> None:
        """Delete objects from the vector database.

        Args:
            ids (List[str]): A list of object IDs to delete.

        Examples:
            >>> vector_db = MyVectorDBImplementation()
            >>> async with vector_db as vdb:
            >>>     ids_to_delete: List[str] = ["id1", "id2", "id3"]
            >>>     await vdb.delete_objects(ids=ids_to_delete)
        """
        ...

    @abstractmethod
    async def semantic_search(
            self: Self,
            index_name: str,
            embedding_query: List[float],
            max_results: PositiveInt,
            score_threshold: Annotated[PositiveFloat, Field(ge=0.0, le=1.0)],
        ) -> List[SemanticSearchResult]:
        """Perform a semantic search in the vector database.

        Args:
            index_name (str): The name of the index to search in.
            embedding_query (List[float]): The embedding vector to search for. Make sure its dimension matches the index dimension.
            max_results (PositiveInt): The maximum number of results to return.
            score_threshold (PositiveFloat): The minimum similarity score (between 0 and 1) for a result to be included in the results list.

        Returns:
            List[SemanticSearchResult]: A list of SemanticSearchResult objects representing the search results.

        Examples:
            >>> vector_db = MyVectorDBImplementation()
            >>> async with vector_db as vdb:
            >>>     query_embedding: List[float] = [0.1, 0.2, 0.3, ...]  # Ensure the embedding dimension matches the index
            >>>     results: List[SemanticSearchResult] = await vdb.semantic_search(
            >>>         index_name="my_index",
            >>>         embedding_query=query_embedding,
            >>>         max_results=10,
            >>>         score_threshold=0.5,
            >>>     )
        """
        ...

    # @abstractmethod
    # async def filter_search(self: Self) -> ...:
    #     ...