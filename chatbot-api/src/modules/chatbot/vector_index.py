import asyncio
from typing import Any, List, Optional

from llama_index.core import VectorStoreIndex
from llama_index.core.schema import TextNode, BaseNode
from llama_index.core.vector_stores.types import (
    BasePydanticVectorStore,
    VectorStoreQuery,
    VectorStoreQueryResult,
)
from pydantic import PrivateAttr
from redis.asyncio import Redis
from redisvl.index import AsyncSearchIndex
from redisvl.query import VectorQuery
from redisvl.schema import IndexSchema

from dos_utility.utils.redis.env import get_redis_connection_settings

from src.modules.settings import SETTINGS


class _RedisVectorStore(BasePydanticVectorStore):
    """Custom LlamaIndex vector store backed by Redis / redisvl 0.14.x.

    Only implements ``query`` / ``aquery``; add/delete are handled by the
    chatbot-index service and are not needed here.
    """

    stores_text: bool = True
    is_embedding_query: bool = True
    flat_metadata: bool = True

    _schema: IndexSchema = PrivateAttr()
    _redis_url: str = PrivateAttr()

    def __init__(self, schema: IndexSchema, redis_url: str, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._schema = schema
        self._redis_url = redis_url

    @property
    def client(self) -> Any:
        return None

    def add(self, nodes: List[BaseNode], **kwargs: Any) -> List[str]:
        raise NotImplementedError("Indexing is handled by chatbot-index")

    def delete(self, ref_doc_id: str, **kwargs: Any) -> None:
        raise NotImplementedError("Deletion is handled by chatbot-index")

    def query(self, query: VectorStoreQuery, **kwargs: Any) -> VectorStoreQueryResult:
        # Sync fallback — only reached from non-async call paths
        return asyncio.run(self.aquery(query, **kwargs))

    async def aquery(
        self, query: VectorStoreQuery, **kwargs: Any
    ) -> VectorStoreQueryResult:
        if not query.query_embedding:
            return VectorStoreQueryResult(nodes=[], similarities=[], ids=[])

        redis_client = Redis.from_url(self._redis_url)
        try:
            index = AsyncSearchIndex.from_existing(
                name=self._schema.index.name,
                redis_client=redis_client,
            )

            vector_query = VectorQuery(
                vector=query.query_embedding,
                vector_field_name="vector",
                return_fields=["id", "doc_id", "text", "url"],
                num_results=query.similarity_top_k,
            )

            results = await index.aquery(vector_query)
        finally:
            await redis_client.aclose()

        nodes: List[BaseNode] = []
        similarities: List[float] = []
        ids: List[str] = []

        for result in results:
            node = TextNode(
                text=result.get("text", ""),
                id_=result.get("id", ""),
                metadata={
                    "url": result.get("url", ""),
                    "doc_id": result.get("doc_id", ""),
                },
            )
            nodes.append(node)
            # redisvl returns cosine distance (0 = identical); convert to similarity
            dist = float(result.get("vector_distance", 1.0))
            similarities.append(1.0 - dist)
            ids.append(result.get("id", ""))

        return VectorStoreQueryResult(nodes=nodes, similarities=similarities, ids=ids)


def get_redis_schema(index_id: str) -> IndexSchema:
    """Builds the redisvl IndexSchema for a LlamaIndex vector store."""
    return IndexSchema.from_dict(
        {
            "index": {"name": index_id, "prefix": index_id},
            "fields": [
                {"name": "id", "type": "tag"},
                {"name": "doc_id", "type": "tag"},
                {"name": "text", "type": "text"},
                {"name": "url", "type": "text"},
                {
                    "name": "vector",
                    "type": "vector",
                    "attrs": {
                        "dims": SETTINGS.embed_dim,
                        "algorithm": "hnsw",
                        "distance_metric": "cosine",
                    },
                },
            ],
        }
    )


def load_index_redis(index_id: str) -> VectorStoreIndex:
    """Loads an existing vector index from Redis.

    Connects to the Redis instance configured via REDIS_HOST / REDIS_PORT
    environment variables and wraps it in a LlamaIndex VectorStoreIndex ready
    for querying.  The index must already exist (created by chatbot-index).

    Args:
        index_id (str): The Redis index name to load.

    Returns:
        VectorStoreIndex: A LlamaIndex index ready to be used as a query engine.

    Raises:
        ValueError: If the index cannot be loaded from Redis.
    """
    redis_settings = get_redis_connection_settings()
    redis_url = f"redis://{redis_settings.REDIS_HOST}:{redis_settings.REDIS_PORT}"

    try:
        vector_store = _RedisVectorStore(
            schema=get_redis_schema(index_id),
            redis_url=redis_url,
        )

        return VectorStoreIndex.from_vector_store(vector_store=vector_store)

    except Exception as e:
        raise ValueError(f"Error loading index '{index_id}' from Redis: {e}")
