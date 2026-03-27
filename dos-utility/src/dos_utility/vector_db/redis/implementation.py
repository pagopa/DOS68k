import logging

from redis.connection import ConnectionPool
from redis.asyncio import Redis as RedisAsync
from redisvl.index import AsyncSearchIndex
from redisvl.exceptions import RedisSearchError
from redisvl.schema import IndexInfo, IndexSchema, StorageType
from redisvl.schema.fields import VectorIndexAlgorithm, VectorDataType, VectorDistanceMetric
from redisvl.query import VectorQuery, FilterQuery
from redisvl.query.filter import FilterExpression, Tag, Num, Text
from typing import Self, List, Optional, Annotated, Any
from pydantic import Field, PositiveFloat, PositiveInt, PrivateAttr
from llama_index.core.vector_stores.types import (
    VectorStoreQuery,
    VectorStoreQueryResult,
    MetadataFilters,
    FilterOperator,
    FilterCondition,
)
from llama_index.core.schema import TextNode

from ...utils.redis.connection import get_redis_connection_pool
from ..interface import VectorDBInterface, ObjectData, SearchResult
from ..exceptions import IndexCreationException, IndexDeletionException, PutObjectsException, DeleteObjectsException


class RedisVectorDB(VectorDBInterface):
    index_name: Optional[str] = None

    _redis_aclient: RedisAsync = PrivateAttr()

    def model_post_init(self: Self, __context: Any) -> None:  # see VectorDBInterface for why this is used instead of __init__
        connection_pool: ConnectionPool = get_redis_connection_pool()
        self._redis_aclient = RedisAsync(connection_pool=connection_pool)

    @property
    def client(self: Self) -> RedisAsync:
        return self._redis_aclient

    async def __aenter__(self: Self) -> Self:
        return self

    async def __aexit__(self: Self, exc_type, exc_val, exc_tb) -> None:
        await self._redis_aclient.aclose()

    async def __get_index(self: Self, index_name: str) -> AsyncSearchIndex:
        return await AsyncSearchIndex.from_existing(name=index_name, redis_client=self._redis_aclient)

    async def create_index(self: Self, index_name: str, vector_dim: int) -> None:
        try:
            index_info: IndexInfo = IndexInfo(
                name=index_name,
                prefix=f"{index_name}/vector",
                storage_type=StorageType.JSON,
            )
            index_schema: IndexSchema = IndexSchema(
                index=index_info,
                fields=[
                    {"name": "id", "type": "tag", "attrs": {"sortable": False}},
                    {"name": "doc_id", "type": "tag", "attrs": {"sortable": False}},
                    {"name": "text", "type": "text", "attrs": {"weight": 1.0}},
                    {
                        "name": "vector",
                        "type": "vector",
                        "attrs": {
                            "dims": vector_dim,
                            "algorithm": VectorIndexAlgorithm.FLAT,
                            "datatype": VectorDataType.FLOAT32,
                            "distance_metric": VectorDistanceMetric.COSINE,
                        },
                    },
                ],
            )
            index: AsyncSearchIndex = AsyncSearchIndex(
                schema=index_schema,
                redis_client=self._redis_aclient,
                validate_on_load=True,
            )

            await index.create(overwrite=False)

            logging.info(f"Index '{index_name}' created successfully.")
        except Exception as e:
            raise IndexCreationException(msg=str(e))

    async def delete_index(self: Self, index_name: str) -> None:
        try:
            index: AsyncSearchIndex = await self.__get_index(index_name=index_name)

            try:
                deleted: bool = await index.delete(drop=True) # Delete index and all associated data

                if deleted is False:
                    raise Exception(f"Failed to delete index '{index_name}'")

                logging.info(f"Index '{index_name}' deleted successfully.")
            except RedisSearchError as e:
                if "Error while deleting index: Unknown Index name" == str(e):
                    logging.warning(f"Index '{index_name}' does not exist. Nothing to delete.")

                    pass
                else:
                    logging.error(f"Failed to delete index '{index_name}': {e}")

                    raise
        except Exception as e:
            raise IndexDeletionException(msg=str(e))

    async def get_indexes(self: Self) -> List[str]:
        indexes: List[bytes] = await self._redis_aclient.execute_command("FT._LIST")

        return [index.decode("utf-8") for index in indexes]

    async def put_objects(self: Self, index_name: str, data: List[ObjectData], custom_keys: Optional[List[str]]=None) -> List[str]:
        try:
            index: AsyncSearchIndex = await self.__get_index(index_name=index_name)

            if custom_keys is not None:
                keys: List[str] = await index.load(data=[obj.model_dump() for obj in data], keys=custom_keys)
            else:
                keys: List[str] = await index.load(data=[obj.model_dump() for obj in data])

            logging.info(f"Objects added to index '{index_name}' successfully.")

            return keys
        except Exception as e:
            raise PutObjectsException(msg=str(e))

    async def delete_objects(self: Self, index_name: str, ids: List[str]) -> None:
        try:
            index: AsyncSearchIndex = await self.__get_index(index_name=index_name)

            _ = await index.drop_keys(keys=ids)

            logging.info(f"Objects deleted from index '{index_name}' successfully.")
        except Exception as e:
            raise DeleteObjectsException(msg=str(e))

    async def semantic_search(
            self: Self,
            index_name: str,
            embedding_query: List[float],
            max_results: PositiveInt,
            score_threshold: Annotated[PositiveFloat, Field(ge=0.0, le=1.0)],
            filters: Optional[MetadataFilters] = None,
        ) -> List[SearchResult]:
        index: AsyncSearchIndex = await self.__get_index(index_name=index_name)

        query: VectorQuery = VectorQuery(
            vector=embedding_query,
            vector_field_name="embedding",
            num_results=max_results,
            return_fields=["id", "filename", "chunk_id", "content"],
            return_score=True,
            filter_expression=self.__build_filter_expression(filters) if filters else None,
        )
        results = await index.query(query=query)

        return [
            SearchResult(
                id=result["id"],
                filename=result["filename"],
                chunk_id=result["chunk_id"],
                content=result["content"],
                score=1 - float(result["vector_distance"]), # Redis returns distance, we convert it to similarity score between 0 and 1
            )
            for result in results
            if (1 - float(result["vector_distance"])) >= score_threshold
        ]

    async def filter_search(
            self: Self,
            index_name: str,
            filters: MetadataFilters,
            max_results: PositiveInt,
        ) -> List[SearchResult]:
        index: AsyncSearchIndex = await self.__get_index(index_name=index_name)

        query: FilterQuery = FilterQuery(
            filter_expression=self.__build_filter_expression(filters),
            return_fields=["id", "filename", "chunk_id", "content"],
            num_results=max_results,
        )
        results = await index.query(query=query)

        return [
            SearchResult(
                id=r.get("id", ""),
                filename=r.get("filename", ""),
                chunk_id=r.get("chunk_id", 0),
                content=r.get("content", ""),
                score=None,
            )
            for r in results
        ]

    def __build_filter_expression(self: Self, metadata_filters: Optional[MetadataFilters]) -> FilterExpression:
        if not metadata_filters or not metadata_filters.filters:
            return FilterExpression("*")

        filter_expressions = []
        for f in metadata_filters.filters:
            if isinstance(f, MetadataFilters):
                filter_expressions.append(self.__build_filter_expression(f))
                continue

            op = f.operator
            if op in (FilterOperator.TEXT_MATCH, FilterOperator.TEXT_MATCH_INSENSITIVE):
                expr = Text(f.key) % f.value
            elif op in (FilterOperator.GT, FilterOperator.LT, FilterOperator.GTE, FilterOperator.LTE):
                num = Num(f.key)
                op_map = {
                    FilterOperator.GT:  lambda n, v: n > v,
                    FilterOperator.LT:  lambda n, v: n < v,
                    FilterOperator.GTE: lambda n, v: n >= v,
                    FilterOperator.LTE: lambda n, v: n <= v,
                }
                expr = op_map[op](num, f.value)
            else:
                tag = Tag(f.key)
                expr = (tag != f.value) if op in (FilterOperator.NE, FilterOperator.NIN) else (tag == f.value)

            filter_expressions.append(expr)

        combined = filter_expressions[0]
        for expr in filter_expressions[1:]:
            combined = (combined | expr) if metadata_filters.condition == FilterCondition.OR else (combined & expr)
        return combined

    async def aquery(self: Self, query: VectorStoreQuery, **kwargs: Any) -> VectorStoreQueryResult:
        if self.index_name is None:
            raise ValueError("index_name must be set at construction time to use aquery")
        if query.query_embedding is None and not query.filters:
            raise ValueError("Either query_embedding or filters must be provided")

        if query.query_embedding is None:
            results = await self.filter_search(
                index_name=self.index_name,
                filters=query.filters,
                max_results=query.similarity_top_k,
            )
            similarities = None
        else:
            results = await self.semantic_search(
                index_name=self.index_name,
                embedding_query=query.query_embedding,
                max_results=query.similarity_top_k,
                score_threshold=0.0,
                filters=query.filters,
            )
            similarities = [r.score for r in results]

        return VectorStoreQueryResult(
            nodes=[
                TextNode(
                    id_=r.id,
                    text=r.content,
                    metadata={"filename": r.filename, "chunk_id": r.chunk_id},
                )
                for r in results
            ],
            similarities=similarities,
            ids=[r.id for r in results],
        )


def get_redis_vector_db(index_name: Optional[str] = None) -> "RedisVectorDB":
    return RedisVectorDB(index_name=index_name)
