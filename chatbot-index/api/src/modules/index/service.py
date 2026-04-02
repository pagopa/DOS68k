from typing import Self, List, Annotated
from datetime import datetime
from fastapi import Depends, HTTPException, status

from dos_utility.vector_db import VectorDBInterface, get_vector_db, IndexCreationException, IndexDeletionException

from .dto import CreateIndexResponse
from .env import settings


class IndexService:
    def __init__(self: Self, vdb: VectorDBInterface):
        self.vdb: VectorDBInterface = vdb

    async def create_index(self: Self, index_id: str, user_id: str) -> CreateIndexResponse:
        existing_indexes: List[str] = await self.vdb.get_indexes()
        if index_id in existing_indexes:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Index '{index_id}' already exists")

        try:
            await self.vdb.create_index(index_id, settings.embed_dim)
        except IndexCreationException as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

        return CreateIndexResponse(
            index_id=index_id,
            user_id=user_id,
            created_at=datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S"),
        )

    async def delete_index(self: Self, index_id: str) -> None:
        existing_indexes: List[str] = await self.vdb.get_indexes()
        if index_id not in existing_indexes:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Index '{index_id}' not found")

        try:
            await self.vdb.delete_index(index_id)
        except IndexDeletionException as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    async def get_indexes(self: Self) -> List[str]:
        return await self.vdb.get_indexes()


def get_index_service(vdb: Annotated[VectorDBInterface, Depends(dependency=get_vector_db)]) -> IndexService:
    return IndexService(vdb=vdb)
