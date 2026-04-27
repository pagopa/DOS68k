from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

from .interface import VectorDBInterface, ObjectData, SearchResult
from .env import get_vector_db_settings, VectorDBSettings, VectorDBProvider
from .redis import get_redis_vector_db
from .qdrant import get_qdrant_vector_db
from .exceptions import (
    IndexCreationException,
    IndexDeletionException,
    PutObjectsException,
    DeleteObjectsException,
)

__all__ = [
    "VectorDBInterface",
    "ObjectData",
    "SearchResult",
    "get_vector_db_ctx",
    "get_vector_db",
    "get_vector_db_instance",
    "IndexCreationException",
    "IndexDeletionException",
    "PutObjectsException",
    "DeleteObjectsException",
]


def get_vector_db_instance(index_name: Optional[str] = None) -> VectorDBInterface:
    """Return a VectorDB instance directly, without a context manager.

    Intended for use with LlamaIndex (VectorStoreIndex.from_vector_store) where
    the lifecycle is not request-scoped. The client is initialised at construction
    time; no explicit connection step is required before calling async methods.

    Args:
        index_name: Pre-set index name required by the LlamaIndex aquery method.
            Pass None to create an instance for plain method calls where the
            index is specified per-call.

    Examples:
        >>> vdb = get_vector_db_instance(index_name="my_index")
        >>> index = VectorStoreIndex.from_vector_store(vector_store=vdb, embed_model=...)
    """
    settings: VectorDBSettings = get_vector_db_settings()

    if settings.VECTOR_DB_PROVIDER is VectorDBProvider.REDIS:
        return get_redis_vector_db(index_name=index_name)
    elif settings.VECTOR_DB_PROVIDER is VectorDBProvider.QDRANT:
        return get_qdrant_vector_db(index_name=index_name)


@asynccontextmanager
async def get_vector_db_ctx(
    index_name: Optional[str] = None,
) -> AsyncGenerator[VectorDBInterface, None]:
    """Context manager to get the appropriate VectorDB implementation based on settings.

    Args:
        index_name: Optional index name to pre-set on the instance. When omitted,
            each method call must supply its own index_name argument.

    Yields:
        AsyncGenerator[VectorDBInterface, None]: An asynchronous generator yielding the VectorDBInterface implementation

    Examples:
        >>> async with get_vector_db_ctx() as vector_db:
        >>>     await vector_db.create_index(index_name="my_index", vector_dim=128)
    """
    async with get_vector_db_instance(index_name=index_name) as vector_db:
        yield vector_db


#! It's the same of get_vector_db_ctx, but without the @asynccontextmanager decorator (it would fail if called as FastAPI dependency)
async def get_vector_db(
    index_name: Optional[str] = None,
) -> AsyncGenerator[VectorDBInterface, None]:
    """FastAPI dependency to get the appropriate VectorDB implementation based on settings.

    Args:
        index_name: Optional index name to pre-set on the instance.

    Yields:
        AsyncGenerator[VectorDBInterface, None]: An asynchronous generator yielding the VectorDBInterface implementation

    Examples:
        >>> @app.post("/create_index")
        >>> async def create_index(vector_db: Annotated[VectorDBInterface, Depends(get_vector_db)]):
        >>>     await vector_db.create_index(index_name="my_index", vector_dim=128)
    """
    async with get_vector_db_ctx(index_name=index_name) as vector_db:
        yield vector_db
