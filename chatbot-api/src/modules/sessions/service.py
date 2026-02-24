from typing import Self, List, Annotated, Dict, Any, Optional
from datetime import datetime
from fastapi import Depends, HTTPException, status

from ..queries import get_query_repository, QueryRepository
from .repository import SessionRepository, get_session_repository


class SessionService:
    def __init__(self: Self, session_repository: SessionRepository, query_repository: QueryRepository):
        self.session_repository: SessionRepository = session_repository
        self.query_repository: QueryRepository = query_repository

    async def get_sessions(self: Self, user_id: str) -> List[Dict[str, Any]]:
        sessions: List[Dict[str, Any]] = await self.session_repository.get_sessions(user_id=user_id)

        return [
            {
                "id": session["id"],
                "title": session["title"],
                "createdAt": session["createdAt"],
                "expiresAt": datetime.fromtimestamp(float(session["expiresAt"])).isoformat(),
            }
            for session in sessions
        ]

    async def create_session(self: Self, user_id: str, session_data: Dict[str, Any]) -> None:
        await self.session_repository.create_session(user_id=user_id, session_data=session_data)

    async def delete_session(self: Self, session_id: str, user_id: str) -> None:
        # Check whether the session exists and belongs to the user
        session: Optional[Dict[str, Any]] = await self.session_repository.get_session(session_id=session_id, user_id=user_id)

        if session is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

        # Get all queries related to the session to delete
        queries: List[Dict[str, Any]] = await self.query_repository.get_queries(session_id=session_id)

        # Delete all queries related to the session
        for query in queries:
            await self.query_repository.delete_query(query_id=query["id"])

        await self.session_repository.delete_session(session_id=session_id, user_id=user_id)

def get_session_service(
        session_repository: Annotated[SessionRepository, Depends(dependency=get_session_repository)],
        query_repository: Annotated[QueryRepository, Depends(dependency=get_query_repository)],
    ) -> SessionService:
    return SessionService(
        session_repository=session_repository,
        query_repository=query_repository,
    )