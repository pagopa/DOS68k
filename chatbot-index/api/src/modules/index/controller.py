from fastapi import APIRouter, Depends, status
from datetime import datetime
from typing import List, Dict, Any, Annotated

from dos_utility.vector_db import VectorDBInterface, get_vector_db
from ..auth import get_user_id

from .dto import CreateIndexResponse
from .env import settings




router: APIRouter = APIRouter(prefix="/index", tags=["indices"])

@router.post(
    path = "/{index_id}",
    response_model=CreateIndexResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_201_CREATED: {"description": "Index created successfully"},
    },
    summary="Create a new index for the authenticated user",
)
async def post_index(index_id: str, 
                     vdb = Depends(get_vector_db),
                     user = Depends(get_user_id)):
    
    await vdb.create_index(index_id, settings.embed_dim)

    return CreateIndexResponse(
        index_id = index_id,
        user_id = user,
        created_at = datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")
    )



@router.get(
    path = "/all",
    response_model=List[str],
    responses={
    },
    summary="Get all existing indexes",
)
async def get_all_indexes(vdb = Depends(get_vector_db),
                     user = Depends(get_user_id)):
    indexes = await vdb.get_indexes()
    return indexes

