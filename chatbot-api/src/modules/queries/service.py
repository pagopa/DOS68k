import nh3

from typing import List, Self, Annotated, Dict, Any, Optional
from fastapi import Depends, HTTPException, status
from datetime import datetime
from httpx import AsyncClient, Response, Timeout

from ..sessions.repository import get_session_repository, SessionRepository
from ..env import get_masking_settings, get_session_settings, SessionSettings, MaskingSettings
from .repository import QueryRepository, get_query_repository

class QueryService:
    def __init__(self: Self, query_repository: QueryRepository, session_repository: SessionRepository):
        self.query_repository: QueryRepository = query_repository
        self.session_repository: SessionRepository = session_repository
        self.settings: SessionSettings = get_session_settings()
        self.masking_settings: MaskingSettings = get_masking_settings()

    async def __mask_pii(self: Self, text: str) -> str:
        async with AsyncClient(timeout=Timeout(timeout=20.0)) as client:
            response: Response = await client.post(
                url=f"{self.masking_settings.masking_service_url}/mask",
                json={"text": text},
            )

            print(response)

            if response.status_code != status.HTTP_200_OK:
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Masking service error")

        masked_text: str = response.json()

        return masked_text

    async def get_queries(self: Self, session_id: str, user_id: str) -> List[Dict[str, Any]]:
        # Check whether the session exists and belongs to the user
        session: Optional[Dict[str, Any]] = await self.session_repository.get_session(session_id=session_id, user_id=user_id)

        if session is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

        queries: List[Dict[str, Any]] = await self.query_repository.get_queries(session_id=session_id)

        return [
            {
                "id": query["id"],
                "session_id": query["sessionId"],
                "question": query["question"],
                "answer": query["answer"],
                "bad_answer": query["badAnswer"],
                "topic": query["topic"],
                "created_at": query["createdAt"],
                "expires_at": None if query["expiresAt"] is None else datetime.fromtimestamp(float(query["expiresAt"])).isoformat(),
            }
            for query in queries
        ]

    async def create_query(self: Self, session_id: str, user_id: str, question: str) -> None:
        # Check whether the session exists and belongs to the user
        session: Optional[Dict[str, Any]] = await self.session_repository.get_session(session_id=session_id, user_id=user_id)

        if session is None:
            # Create a new session for the user if it doesn't exist, or 
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

        question_cleaned = nh3.clean(html=question) # Sanitize from HTML tags and scripts

        # Get session history
        session_history: List[Dict[str, Any]] = await self.query_repository.get_queries(session_id=session_id)

        #! Simulate LLM call and response generation
        # In a real implementation, you would call your LLM here and generate an answer based on the question and session history
        answer: str = "Simulated answer"
        topic: List[str] = ["simulated", "topic"]

        # Call masking service to mask PII in question/answer before store it
        question_masked: str = question_cleaned
        answer_masked: str = answer

        if self.masking_settings.mask_pii is True:
            question_masked = await self.__mask_pii(text=question_cleaned)
            answer_masked = await self.__mask_pii(text=answer)

        await self.query_repository.create_query(
            session_id=session_id,
            query_data={
                "question": question_masked,
                "answer": answer_masked,
                "expiresAt": session["expiresAt"],
                "topic": topic,
            },
        )

def get_query_service(
        query_repository: Annotated[QueryRepository, Depends(dependency=get_query_repository)],
        session_repository: Annotated[SessionRepository, Depends(dependency=get_session_repository)],
    ) -> QueryService:
    return QueryService(
        query_repository=query_repository,
        session_repository=session_repository,
    )