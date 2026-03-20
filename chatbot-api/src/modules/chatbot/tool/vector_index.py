from llama_index.core import VectorStoreIndex
from llama_index.core.base.embeddings.base import BaseEmbedding
from dos_utility.vector_db.interface import VectorDBInterface


def load_index(vector_db: VectorDBInterface, embed_model: BaseEmbedding) -> VectorStoreIndex:
    """Creates a LlamaIndex VectorStoreIndex from any VectorDBInterface implementation.

    The vector_db instance must have index_name set. The client connection is
    established lazily on the first query.

    Args:
        vector_db (VectorDBInterface): A configured vector database instance with index_name set.
        embed_model (BaseEmbedding): The embedding model used to embed queries at retrieval time.

    Returns:
        VectorStoreIndex: A LlamaIndex index ready to be used as a query engine.
    """
    return VectorStoreIndex.from_vector_store(vector_store=vector_db, embed_model=embed_model)
