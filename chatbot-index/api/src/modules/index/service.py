from logging import Logger
from typing import Self, List, Annotated
from datetime import datetime
from fastapi import Depends, HTTPException, status

from dos_utility.vector_db import (
    VectorDBInterface,
    get_vector_db,
    IndexCreationException,
    IndexDeletionException,
)
from dos_utility.storage import StorageInterface, get_storage
from dos_utility.utils.logger import get_logger

from .dto import CreateIndexResponse
from .env import get_embedding_settings, EmbeddingsSettings
from ...env import get_settings, get_index_bucket_settings, IndexBucketSettings, Settings



class IndexService:
    def __init__(self: Self, vdb: VectorDBInterface, storage: StorageInterface):
        self.vdb: VectorDBInterface = vdb
        self.storage: StorageInterface = storage
        self.settings: Settings = get_settings()
        self.embedding_settings: EmbeddingsSettings = get_embedding_settings()
        self.index_bucket_settings: IndexBucketSettings = get_index_bucket_settings()
        self.logger: Logger = get_logger(name=__file__, level=self.settings.log_level)

    async def verify_index_exists(self: Self, index_id: str) -> None:
        existing_indexes: List[str] = await self.vdb.get_indexes()

        if index_id in existing_indexes:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Index '{index_id}' already exists",
            )

    async def create_index(
        self: Self, index_id: str, user_id: str
    ) -> CreateIndexResponse:
        await self.verify_index_exists(index_id=index_id)

        try:
            await self.vdb.create_index(index_id, self.embedding_settings.embed_dim)
        except IndexCreationException as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
            )

        self.logger.info(f"Index '{index_id}' successfully created")

        return CreateIndexResponse(
            index_id=index_id,
            user_id=user_id,
            created_at=datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S"),
        )

    async def delete_index(self: Self, index_id: str) -> None:
        await self.verify_index_exists(index_id=index_id)

        try:
            await self.vdb.delete_index(index_id)
        except IndexDeletionException as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
            )

        prefix: str = f"{index_id}/"
        objects = self.storage.list_objects(bucket=self.index_bucket_settings.index_documents_bucket_name)
        for obj in objects:
            if obj.key.startswith(prefix):
                self.storage.delete_object(bucket=self.index_bucket_settings.index_documents_bucket_name, name=obj.key)
                self.logger.debug(f"Delete storage object '{obj.key}'")

        self.logger.info(f"Index '{index_id}' successfully deleted")

    async def get_indexes(self: Self) -> List[str]:
        return await self.vdb.get_indexes()


def get_index_service(
    vdb: Annotated[VectorDBInterface, Depends(dependency=get_vector_db)],
    storage: Annotated[StorageInterface, Depends(dependency=get_storage)],
) -> IndexService:
    return IndexService(vdb=vdb, storage=storage)
