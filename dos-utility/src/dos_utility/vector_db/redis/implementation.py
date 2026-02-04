import logging

from redis.asyncio import ConnectionPool, Redis
from redisvl.index import AsyncSearchIndex
from redisvl.exceptions import RedisSearchError
from redisvl.schema import IndexInfo, IndexSchema, StorageType
from redisvl.schema.fields import VectorIndexAlgorithm, VectorDataType, VectorDistanceMetric
from redisvl.query import VectorQuery
from typing import Self, List, Optional, Annotated, Dict, Any
from pydantic import Field, PositiveFloat, PositiveInt

from ...utils.redis.connection import get_redis_connection_pool
from ..interface import VectorDBInterface, ObjectData, SemanticSearchResult


class RedisVectorDB(VectorDBInterface):
    def __get_index(self: Self, index_name: str) -> AsyncSearchIndex:
        return AsyncSearchIndex.from_existing(name=index_name, redis_client=self._redis_client)

    async def __aenter__(self: Self) -> Self:
        connection_pool: ConnectionPool = get_redis_connection_pool()
        self._redis_client: Redis = Redis(connection_pool=connection_pool)

        return self

    async def __aexit__(self: Self, exc_type, exc_val, exc_tb) -> None:
        await self._redis_client.aclose()

    async def create_index(self: Self, index_name: str, vector_dim: int) -> None:
        index_info: IndexInfo = IndexInfo(name=index_name, storage_type=StorageType.JSON)
        index_schema: IndexSchema = IndexSchema(
            index=index_info,
            fields=[
                {"name": "filename", "type": "text"},
                {"name": "chunk_id", "type": "numeric"},
                {"name": "content", "type": "text"},
                {
                    "name": "embedding",
                    "type": "vector",
                    "attrs": {
                        "dims": vector_dim,
                        "algorithm": VectorIndexAlgorithm.HNSW,
                        "datatype": VectorDataType.FLOAT32,
                        "distance_metric": VectorDistanceMetric.COSINE,
                    },
                },
            ],
        )
        index: AsyncSearchIndex = AsyncSearchIndex(
            schema=index_schema,
            redis_client=self._redis_client,
            validate_on_load=True,
        )

        await index.create(overwrite=False)

        logging.info(f"Index '{index_name}' created successfully.")

    async def delete_index(self: Self, index_name: str) -> None:
        index: AsyncSearchIndex = self.__get_index(index_name=index_name)

        try:
            deleted: bool = await index.delete(drop=True) # Delete index and all associated data

            logging.info(f"Index '{index.name}' deleted successfully.")
        except RedisSearchError as e:
            if "Error while deleting index: Unknown Index name" == str(e):
                logging.warning(f"Index '{index.name}' does not exist. Nothing to delete.")

                pass
            else:
                logging.error(f"Failed to delete index '{index.name}': {e}")

                raise

        if deleted is False:
            raise Exception(f"Failed to delete index '{index_name}'")

    async def get_indexes(self: Self) -> List[str]:
        indexes: List[bytes] = await self._redis_client.execute_command("FT._LIST")

        return [index.decode("utf-8") for index in indexes]

    async def put_objects(self: Self, index_name: str, data: List[ObjectData], custom_keys: Optional[List[str]]=None) -> List[str]:
        index: AsyncSearchIndex = self.__get_index(index_name=index_name)

        if custom_keys is not None:
            keys: List[str] = await index.load(data=[obj.model_dump() for obj in data], keys=custom_keys)
        else:
            keys: List[str] = await index.load(data=[obj.model_dump() for obj in data])

        logging.info(f"Objects added to index '{index_name}' successfully.")

        return keys

    async def delete_objects(self: Self, index_name: str, ids: List[str]) -> None:
        index: AsyncSearchIndex = self.__get_index(index_name=index_name)
        _ = await index.drop_keys(keys=ids)

        logging.info(f"Objects deleted from index '{index_name}' successfully.")

    async def semantic_search(
            self: Self,
            index_name: str,
            embedding_query: List[float],
            max_results: PositiveInt,
            score_threshold: Annotated[PositiveFloat, Field(ge=0.0, le=1.0)],
        ) -> List[SemanticSearchResult]:
        index: AsyncSearchIndex = self.__get_index(index_name=index_name)
        query: VectorQuery = VectorQuery(
            vector=embedding_query,
            vector_field_name="embedding",
            num_results=max_results,
            return_fields=["filename", "chunk_id", "content"],
            return_score=True,
        )
        results: List[Dict[str, Any]] = await index.search(query=query)

        return [
            SemanticSearchResult(
                id=result["id"],
                filename=result["filename"],
                chunk_id=result["chunk_id"],
                content=result["content"],
                score=1 - float(result["vector_distance"]), # Redis returns distance, we convert it to similarity score between 0 and 1
            )
            for result in results
            if (1 - float(result["vector_distance"])) >= score_threshold
        ]

def get_redis_vector_db() -> RedisVectorDB:
    return RedisVectorDB()
