from llama_index.core import VectorStoreIndex, StorageContext
from llama_index.vector_stores.redis import RedisVectorStore
from redisvl.schema import IndexSchema

from dos_utility.utils.redis.env import get_redis_connection_settings

from src.modules.settings import SETTINGS


def get_redis_schema(index_id: str) -> IndexSchema:
    """Builds the redisvl IndexSchema for a LlamaIndex vector store.

    The schema must mirror the one used during indexing in chatbot-index.

    Args:
        index_id (str): The Redis index name (e.g. SETTINGS.devportal_index_id).

    Returns:
        IndexSchema: The redisvl schema for the given index.
    """
    return IndexSchema.from_dict(
        {
            "index": {"name": index_id, "prefix": index_id},
            "fields": [
                {"name": "id", "type": "tag"},
                {"name": "doc_id", "type": "tag"},
                {"name": "text", "type": "text"},
                # Metadata field required by _get_response_json to build source links
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
        redis_vector_store = RedisVectorStore(
            schema=get_redis_schema(index_id),
            redis_url=redis_url,
            overwrite=False,
        )

        storage_context = StorageContext.from_defaults(vector_store=redis_vector_store)

        index = VectorStoreIndex.from_vector_store(
            vector_store=redis_vector_store,
            storage_context=storage_context,
        )

        return index

    except Exception as e:
        raise ValueError(f"Error loading index '{index_id}' from Redis: {e}")
