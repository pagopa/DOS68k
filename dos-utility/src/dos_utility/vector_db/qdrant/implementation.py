import asyncio
import logging

from uuid import uuid4
from asyncio import AbstractEventLoop
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import VectorParams, Distance, Datatype, UpdateStatus
from qdrant_client.conversions.common_types import UpdateResult, CollectionsResponse, PointStruct
from qdrant_client.conversions.common_types import QueryResponse
from typing import Self, List, Optional, Annotated
from pydantic import Field, PositiveInt, PositiveFloat

from ..interface import VectorDBInterface, ObjectData, SemanticSearchResult
from .env import QdrantVectorDBSettings, get_qdrant_vector_db_settings


class QdrantVectorDB(VectorDBInterface):
    def __init__(self: Self):
        self._settings: QdrantVectorDBSettings = get_qdrant_vector_db_settings()

    async def __aenter__(self: Self) -> Self:
        loop: AbstractEventLoop = asyncio.get_event_loop()
        self._client: AsyncQdrantClient = await loop.run_in_executor(
            None,
            lambda: AsyncQdrantClient(f"http://{self._settings.QDRANT_HOST}:{self._settings.QDRANT_PORT}"),
        )

        return self

    async def __aexit__(self: Self, exc_type, exc_val, exc_tb) -> None:
        await self._client.close()

    async def create_index(self: Self, index_name: str, vector_dim: int) -> None:
        if not await self._client.collection_exists(collection_name=index_name):
            created: bool = await self._client.create_collection(
                collection_name=index_name,
                vectors_config={
                    "embedding": VectorParams(
                        size=vector_dim,
                        distance=Distance.COSINE,
                        datatype=Datatype.FLOAT32,
                    )
                },
            )

            if created is False:
                raise Exception(f"Failed to create index '{index_name}'")

            logging.info(f"Index '{index_name}' created successfully.")
        else:
            logging.info(f"Index '{index_name}' already exists.")

    async def delete_index(self: Self, index_name: str) -> None:
        deleted: bool = await self._client.delete_collection(collection_name=index_name)

        if deleted is False:
            raise Exception(f"Failed to delete index '{index_name}'")

        logging.info(f"Index '{index_name}' deleted successfully.")

    async def get_indexes(self: Self) -> List[str]:
        collections: CollectionsResponse = await self._client.get_collections()

        return [collection.name for collection in collections.collections]

    async def put_objects(self: Self, index_name: str, data: List[ObjectData], custom_keys: Optional[List[str]]=None) -> List[str]:
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
        else:
            raise Exception(f"Failed to add objects to index '{index_name}'")

    # async def get_objects(self: Self, index_name: str, ids: List[str]) -> ...:
    #     return await self._client.retrieve(collection_name=index_name, ids=ids)

    async def delete_objects(self: Self, index_name: str, ids: List[str]) -> None:
        result: UpdateResult = await self._client.delete(
            collection_name=index_name,
            points_selector=ids,
            wait=True
        )

        if result.status is UpdateStatus.COMPLETED:
            logging.info(f"Objects deleted from index '{index_name}' successfully.")
        else:
            raise Exception(f"Failed to delete objects from index '{index_name}'")

    async def semantic_search(
            self: Self,
            index_name: str,
            embedding_query: List[float],
            max_results: PositiveInt,
            score_threshold: Annotated[PositiveFloat, Field(ge=0.0, le=1.0)],
        ) -> List[SemanticSearchResult]:
        result: QueryResponse = await self._client.query_points(
            collection_name=index_name,
            query=embedding_query,
            limit=max_results,
            using="embedding",
        )

        return [
            SemanticSearchResult(
                id=point.id,
                filename=point.payload["filename"],
                chunk_id=point.payload["chunk_id"],
                content=point.payload["content"],
                score=point.score,
            )
            for point in result.points
            if point.score >= score_threshold
        ]


def get_qdrant_vector_db() -> QdrantVectorDB:
    return QdrantVectorDB()