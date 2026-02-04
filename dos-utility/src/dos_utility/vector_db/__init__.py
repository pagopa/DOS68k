from contextlib import asynccontextmanager
from typing import AsyncGenerator

from .interface import VectorDBInterface, ObjectData, SemanticSearchResult
from .env import get_vector_db_settings, VectorDBSettings, VectorDBProvider
from .redis import get_redis_vector_db
from .qdrant import get_qdrant_vector_db

__all__ = [
    "VectorDBInterface",
    "ObjectData",
    "SemanticSearchResult",
    "get_vector_db_ctx",
    "get_vector_db",
]

@asynccontextmanager
async def get_vector_db_ctx() -> AsyncGenerator[VectorDBInterface, None]:
    """Context manager to get the appropriate VectorDB implementation based on settings.

    Yields:
        AsyncGenerator[VectorDBInterface, None]: An asynchronous generator yielding the VectorDBInterface implementation

    Examples:
        >>> async with get_vector_db_ctx() as vector_db:
        >>>     await vector_db.create_index(index_name="my_index", vector_dim=128)
    """
    settings: VectorDBSettings = get_vector_db_settings()

    if settings.VECTOR_DB_PROVIDER is VectorDBProvider.REDIS:
        vector_db: VectorDBInterface = get_redis_vector_db()
    elif settings.VECTOR_DB_PROVIDER is VectorDBProvider.QDRANT:
        vector_db: VectorDBInterface = get_qdrant_vector_db()

    async with vector_db as vdb:
        yield vdb

async def get_vector_db() -> AsyncGenerator[VectorDBInterface, None]:
    """FastAPI dependency to get the appropriate VectorDB implementation based on settings.

    Yields:
        AsyncGenerator[VectorDBInterface, None]: An asynchronous generator yielding the VectorDBInterface implementation

    Examples:
        >>> @app.post("/create_index")
        >>> async def create_index(vector_db: Annotated[VectorDBInterface, Depends(get_vector_db)]):
        >>>     await vector_db.create_index(index_name="my_index", vector_dim=128)
    """
    async with get_vector_db_ctx() as vector_db:
        yield vector_db
