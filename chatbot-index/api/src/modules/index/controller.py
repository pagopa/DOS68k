from fastapi import APIRouter, Depends, status
from typing import List, Annotated

from .dto import CreateIndexResponse
from .service import IndexService, get_index_service
from ..auth import get_user_id


router: APIRouter = APIRouter(prefix="/index", tags=["indexes"])


@router.post(
    path="/{index_id}",
    response_model=CreateIndexResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_201_CREATED: {"description": "Index created successfully"},
        status.HTTP_409_CONFLICT: {"description": "Index already exists"},
    },
    summary="Create a new index for the authenticated user",
)
async def post_index(
    index_id: str,
    service: Annotated[IndexService, Depends(dependency=get_index_service)],
    user: Annotated[str, Depends(dependency=get_user_id)],
) -> CreateIndexResponse:
    return await service.create_index(index_id=index_id, user_id=user)


@router.delete(
    path="/{index_id}",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {"description": "Index deleted successfully"},
        status.HTTP_404_NOT_FOUND: {"description": "Index not found"},
    },
    dependencies=[Depends(dependency=get_user_id)],
    summary="Delete an existing index",
)
async def delete_index(
    index_id: str,
    service: Annotated[IndexService, Depends(dependency=get_index_service)],
) -> dict:
    await service.delete_index(index_id=index_id)
    return {"message": f"Index '{index_id}' deleted successfully"}


@router.get(
    path="/all",
    response_model=List[str],
    responses={
        status.HTTP_200_OK: {"description": "Indexes retrieved successfully"},
    },
    dependencies=[Depends(dependency=get_user_id)],
    summary="Get all existing indexes",
)
async def get_all_indexes(
    service: Annotated[IndexService, Depends(dependency=get_index_service)],
) -> List[str]:
    return await service.get_indexes()
