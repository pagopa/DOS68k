import logging

from uuid import uuid4
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import (
    VectorParams, Distance, Datatype, UpdateStatus,
    Filter, FieldCondition, MatchValue, MatchAny, MatchText, Range,
)
from qdrant_client.conversions.common_types import UpdateResult, CollectionsResponse, PointStruct
from qdrant_client.conversions.common_types import QueryResponse
from typing import Self, List, Optional, Annotated, Any
from pydantic import Field, PositiveInt, PositiveFloat, PrivateAttr
from llama_index.core.vector_stores.types import (
    VectorStoreQuery, VectorStoreQueryResult,
    MetadataFilters, FilterOperator, FilterCondition,
)
from llama_index.core.schema import TextNode

from ..interface import VectorDBInterface, ObjectData, SearchResult
from ..exceptions import IndexCreationException, IndexDeletionException, PutObjectsException, DeleteObjectsException
from .env import QdrantVectorDBSettings, get_qdrant_vector_db_settings


class QdrantVectorDB(VectorDBInterface):
    index_name: Optional[str] = None

    _settings: QdrantVectorDBSettings = PrivateAttr()
    _client: Optional[AsyncQdrantClient] = PrivateAttr(default=None)

    def model_post_init(self, __context: Any) -> None:  # see VectorDBInterface for why this is used instead of __init__
        self._settings = get_qdrant_vector_db_settings()
        self._client = AsyncQdrantClient(f"http://{self._settings.QDRANT_HOST}:{self._settings.QDRANT_PORT}")

    @property
    def client(self) -> AsyncQdrantClient:
        return self._client

    async def __aenter__(self: Self) -> Self:
        return self

    async def __aexit__(self: Self, exc_type, exc_val, exc_tb) -> None:
        await self._client.close()

    async def create_index(self: Self, index_name: str, vector_dim: int) -> None:
        try:
            if not await self._client.collection_exists(collection_name=index_name):
                created: bool = await self._client.create_collection(
                    collection_name=index_name,
                    vectors_config={
                        "vector": VectorParams(
                            size=vector_dim,
                            distance=Distance.COSINE,
                            datatype=Datatype.FLOAT32,
                        )
                    },
                )

                if created is False:
                    raise Exception(f"Qdrant gave a negative output when creating index '{index_name}'")

                logging.info(f"Index '{index_name}' created successfully.")
            else:
                logging.info(f"Index '{index_name}' already exists.")
        except Exception as e:
            raise IndexCreationException(msg=str(e))

    async def delete_index(self: Self, index_name: str) -> None:
        try:
            deleted: bool = await self._client.delete_collection(collection_name=index_name)

            if deleted is False:
                raise Exception(f"Qdrant gave a negative output when deleting index '{index_name}'")

            logging.info(f"Index '{index_name}' deleted successfully.")
        except Exception as e:
            raise IndexDeletionException(msg=str(e))

    async def get_indexes(self: Self) -> List[str]:
        collections: CollectionsResponse = await self._client.get_collections()

        return [collection.name for collection in collections.collections]

    async def put_objects(self: Self, index_name: str, data: List[ObjectData], custom_keys: Optional[List[str]]=None) -> List[str]:
        try:
            if custom_keys is not None:
                ids: List[str] = custom_keys
            else:
                ids: List[str] = [uuid4().hex for _ in data]

            result: UpdateResult = await self._client.upsert(
                collection_name=index_name,
                points=[
                    PointStruct(
                        id=ids[i],
                        vector=point.embedding,
                        payload={
                            "filename": point.filename,
                            "chunk_id": point.chunk_id,
                            "content": point.content,
                        },
                    )
                    for i, point in enumerate(data)
                ],
                wait=True,
            )

            if result.status is UpdateStatus.COMPLETED:
                logging.info(f"Objects added to index '{index_name}' successfully.")

                return ids

            raise Exception(f"Adding objects to index '{index_name}' did not complete successfully.")
        except Exception as e:
            raise PutObjectsException(msg=str(e))

    async def delete_objects(self: Self, index_name: str, ids: List[str]) -> None:
        try:
            result: UpdateResult = await self._client.delete(
                collection_name=index_name,
                points_selector=ids,
                wait=True
            )

            if result.status is UpdateStatus.COMPLETED:
                logging.info(f"Objects deleted from index '{index_name}' successfully.")
            else:
                raise Exception(f"Deleting objects from index '{index_name}' did not complete successfully.")
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
        result: QueryResponse = await self._client.query_points(
            collection_name=index_name,
            query=embedding_query,
            query_filter=self._build_filter_condition(filters),
            limit=max_results,
            using="embedding",
        )

        return [
            SearchResult(
                id=str(point.id),
                filename=point.payload["filename"],
                chunk_id=point.payload["chunk_id"],
                content=point.payload["content"],
                score=point.score,
            )
            for point in result.points
            if point.score >= score_threshold
        ]

    async def filter_search(
            self: Self,
            index_name: str,
            filters: MetadataFilters,
            max_results: PositiveInt,
        ) -> List[SearchResult]:
        records, _ = await self._client.scroll(
            collection_name=index_name,
            scroll_filter=self._build_filter_condition(filters),
            limit=max_results,
            with_payload=True,
        )

        return [
            SearchResult(
                id=str(r.id),
                filename=r.payload.get("filename", ""),
                chunk_id=r.payload.get("chunk_id", 0),
                content=r.payload.get("content", ""),
                score=None,
            )
            for r in records
        ]

    def _build_filter_condition(self: Self, metadata_filters: Optional[MetadataFilters]) -> Optional[Filter]:
        if not metadata_filters or not metadata_filters.filters:
            return None

        positive = []
        negative = []

        for f in metadata_filters.filters:
            if isinstance(f, MetadataFilters):
                nested = self._build_filter_condition(f)
                if nested:
                    positive.append(nested)
                continue

            op = f.operator
            if op == FilterOperator.NE:
                negative.append(FieldCondition(key=f.key, match=MatchValue(value=f.value)))
            elif op == FilterOperator.NIN:
                vals = f.value if isinstance(f.value, list) else [f.value]
                negative.append(FieldCondition(key=f.key, match=MatchAny(any=vals)))
            elif op in (FilterOperator.TEXT_MATCH, FilterOperator.TEXT_MATCH_INSENSITIVE):
                positive.append(FieldCondition(key=f.key, match=MatchText(text=str(f.value))))
            elif op in (FilterOperator.IN, FilterOperator.ANY):
                vals = f.value if isinstance(f.value, list) else [f.value]
                positive.append(FieldCondition(key=f.key, match=MatchAny(any=vals)))
            elif op == FilterOperator.GT:
                positive.append(FieldCondition(key=f.key, range=Range(gt=float(f.value))))
            elif op == FilterOperator.LT:
                positive.append(FieldCondition(key=f.key, range=Range(lt=float(f.value))))
            elif op == FilterOperator.GTE:
                positive.append(FieldCondition(key=f.key, range=Range(gte=float(f.value))))
            elif op == FilterOperator.LTE:
                positive.append(FieldCondition(key=f.key, range=Range(lte=float(f.value))))
            elif op == FilterOperator.IS_EMPTY:
                positive.append(FieldCondition(key=f.key, is_empty=True))
            else:  # EQ, CONTAINS, ALL
                positive.append(FieldCondition(key=f.key, match=MatchValue(value=f.value)))

        if not positive and not negative:
            return None

        if metadata_filters.condition == FilterCondition.OR:
            should = list(positive)
            for neg in negative:
                should.append(Filter(must_not=[neg]))
            return Filter(should=should or None)
        else:
            return Filter(must=positive or None, must_not=negative or None)

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


def get_qdrant_vector_db(index_name: Optional[str] = None) -> "QdrantVectorDB":
    return QdrantVectorDB(index_name=index_name)
