from typing import Self, List, Annotated, Dict, Any, Optional
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status

from .env import get_session_settings, SessionSettings
from .repository import SessionRepository, get_session_repository
from ..queries.repository import get_query_repository, QueryRepository
from ..utils import format_expiration_dt


class SessionService:
    def __init__(
        self: Self,
        session_repository: SessionRepository,
        query_repository: QueryRepository,
    ):
        self.session_repository: SessionRepository = session_repository
        self.query_repository: QueryRepository = query_repository
        self.settings: SessionSettings = get_session_settings()

    async def get_session(self: Self, session_id: str, user_id: str) -> Dict[str, Any]:
        session: Optional[Dict[str, Any]] = await self.session_repository.get_session(
            session_id=session_id, user_id=user_id
        )

        if session is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Session not found"
            )

        return {
            "id": session["id"],
            "user_id": session["userId"],
            "title": session["title"],
            "created_at": session["createdAt"],
            "expires_at": format_expiration_dt(session["expiresAt"]),
        }

    async def get_sessions(self: Self, user_id: str) -> List[Dict[str, Any]]:
        sessions: List[Dict[str, Any]] = await self.session_repository.get_sessions(
            user_id=user_id
        )

        return [
            {
                "id": session["id"],
                "user_id": session["userId"],
                "title": session["title"],
                "created_at": session["createdAt"],
                "expires_at": format_expiration_dt(session["expiresAt"]),
            }
            for session in sessions
        ]

    async def create_session(
        self: Self, user_id: str, session_data: Dict[str, Any], is_temporary: bool
    ) -> Dict[str, Any]:
        now: datetime = datetime.now()
        expiration_dt: Optional[int] = (
            None
            if is_temporary is False
            else int(
                (
                    now + timedelta(days=self.settings.SESSION_EXPIRATION_DAYS)
                ).timestamp()
            )
        )

        item: Dict[str, Any] = await self.session_repository.create_session(
            user_id=user_id,
            session_data={
                "expiresAt": expiration_dt,
                **session_data,
            },
        )

        return {
            "id": item["id"],
            "user_id": item["userId"],
            "title": item["title"],
            "created_at": item["createdAt"],
            "expires_at": format_expiration_dt(item["expiresAt"]),
        }

    async def __delete_session_queries(self: Self, session_id: str) -> None:
        # Get all queries related to the session to delete
        queries: List[Dict[str, Any]] = await self.query_repository.get_queries(
            session_id=session_id
        )

        # Delete all queries related to the session
        for query in queries:
            await self.query_repository.delete_query(
                query_id=query["id"], session_id=session_id
            )

    async def clear_session(
        self: Self, session_id: str, user_id: str
    ) -> Dict[str, Any]:
        # Check whether the session exists and belongs to the user
        session: Optional[Dict[str, Any]] = await self.session_repository.get_session(
            session_id=session_id, user_id=user_id
        )

        if session is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Session not found"
            )

        await self.__delete_session_queries(session_id=session_id)

        return session

    async def delete_session(self: Self, session_id: str, user_id: str) -> None:
        # Check whether the session exists and belongs to the user
        session: Optional[Dict[str, Any]] = await self.session_repository.get_session(
            session_id=session_id, user_id=user_id
        )

        if session is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Session not found"
            )

        await self.__delete_session_queries(session_id=session_id)
        await self.session_repository.delete_session(
            session_id=session_id, user_id=user_id
        )


def get_session_service(
    session_repository: Annotated[
        SessionRepository, Depends(dependency=get_session_repository)
    ],
    query_repository: Annotated[
        QueryRepository, Depends(dependency=get_query_repository)
    ],
) -> SessionService:
    return SessionService(
        session_repository=session_repository,
        query_repository=query_repository,
    )
