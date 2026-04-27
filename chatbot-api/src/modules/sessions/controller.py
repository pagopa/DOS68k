from uuid import UUID
from typing import Annotated, List, Dict, Any
from fastapi import APIRouter, Depends, status

from dos_utility.auth import get_user, User

from .service import SessionService, get_session_service
from .dto import CreateSessionDTO, SessionResponseDTO


router: APIRouter = APIRouter(prefix="/sessions", tags=["Sessions"])


@router.get(
    path="/all",
    response_model=List[SessionResponseDTO],
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {"description": "Sessions retrieved successfully"},
    },
    summary="Get all sessions for the authenticated user",
)
async def get_sessions(
        session_service: Annotated[SessionService, Depends(dependency=get_session_service)],
        user: Annotated[User, Depends(dependency=get_user)],
    ) -> List[Dict[str, Any]]:
    return await session_service.get_sessions(user_id=user.id)


@router.get(
    path="/{session_id}",
    response_model=SessionResponseDTO,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {"description": "Session retrieved successfully"},
        status.HTTP_404_NOT_FOUND: {"description": "Session not found"},
    },
    summary="Get a session by its ID",
)
async def get_session(
        session_service: Annotated[SessionService, Depends(dependency=get_session_service)],
        user: Annotated[User, Depends(dependency=get_user)],
        session_id: UUID,
    ) -> Dict[str, Any]:
    return await session_service.get_session(session_id=str(session_id), user_id=user.id)

@router.post(
    path="",
    response_model=SessionResponseDTO,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_201_CREATED: {"description": "Session created successfully"},
    },
    summary="Create a new session for the authenticated user",
)
async def create_session(
        session_service: Annotated[SessionService, Depends(dependency=get_session_service)],
        user: Annotated[User, Depends(dependency=get_user)],
        create_session_dto: CreateSessionDTO,
    ) -> Dict[str, Any]:
    return await session_service.create_session(
        user_id=user.id,
        session_data={"title": create_session_dto.title},
        is_temporary=create_session_dto.is_temporary,
    )


@router.post(
    path="/{session_id}/clear",
    response_model=SessionResponseDTO,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {"description": "Session cleared successfully"},
    },
    summary="Clear the selected session for the authenticated user",
)
async def clear_session(
        session_service: Annotated[SessionService, Depends(dependency=get_session_service)],
        user: Annotated[User, Depends(dependency=get_user)],
        session_id: UUID,
    ) -> Dict[str, Any]:
    return await session_service.clear_session(session_id=str(session_id), user_id=user.id)

@router.delete(
    path="/{session_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_204_NO_CONTENT: {"description": "Session deleted successfully"},
        status.HTTP_404_NOT_FOUND: {"description": "Session not found"},
    },
    summary="Delete a session by its ID",
)
async def delete_session(
        session_service: Annotated[SessionService, Depends(dependency=get_session_service)],
        user: Annotated[User, Depends(dependency=get_user)],
        session_id: UUID,
    ) -> None:
    await session_service.delete_session(session_id=str(session_id), user_id=user.id)
