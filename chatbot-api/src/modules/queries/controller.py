from fastapi import APIRouter, Depends, status
from typing import List, Dict, Any, Annotated

from ..auth import get_user_id
from .service import QueryService, get_query_service
from .dto import QueryResponseDTO, CreateQueryDTO

router: APIRouter = APIRouter(prefix="/queries", tags=["Queries"])

@router.get(
    path="/{session_id}",
    response_model=List[QueryResponseDTO],
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {"description": "Queries retrieved successfully"},
        status.HTTP_404_NOT_FOUND: {"description": "Session not found"},
    },
    summary="Get queries for a session",
)
async def get_queries(
        query_service: Annotated[QueryService, Depends(dependency=get_query_service)],
        user_id: Annotated[str, Depends(dependency=get_user_id)],
        session_id: str,
    ) -> List[Dict[str, Any]]:
    return await query_service.get_queries(session_id=session_id, user_id=user_id)

@router.post(
    path="/{session_id}",
    # response_model=QueryResponseDTO,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_201_CREATED: {"description": "Query created successfully"},
        status.HTTP_404_NOT_FOUND: {"description": "Session not found"},
        status.HTTP_410_GONE: {"description": "Session expired"},
    },
    summary="Create a new query for a session",
)
async def create_query(
        query_service: Annotated[QueryService, Depends(dependency=get_query_service)],
        user_id: Annotated[str, Depends(dependency=get_user_id)],
        query_data: CreateQueryDTO,
        session_id: str,
    ):
    await query_service.create_query(session_id=session_id, user_id=user_id, question=query_data.question)