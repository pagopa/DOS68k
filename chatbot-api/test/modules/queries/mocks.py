from typing import Any, Dict, List
from fastapi import HTTPException, status

def get_query_service_get_queries_200_mock():
    class QueryServiceMock:
        async def get_queries(self, session_id: str, user_id: str) -> List[Dict[str, Any]]:
            return [
                {
                    "id": "03084655-d5c4-42b4-b39a-7097f4a5ed1f",
                    "session_id": "03084655-d5c4-42b4-b39a-7097f4a5ed1f",
                    "question": "What is the capital of France?",
                    "answer": "The capital of France is Paris.",
                    "bad_answer": False,
                    "topic": ["geography", "capital cities"],
                    "created_at": "2024-06-01T12:00:00Z",
                    "expires_at": "2024-06-01T13:00:00Z",
                }
            ]

    return QueryServiceMock()

def get_query_service_get_queries_404_mock():
    class QueryServiceMock:
        async def get_queries(self, session_id: str, user_id: str) -> List[Dict[str, Any]]:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    return QueryServiceMock()

def get_query_service_create_query_201_mock():
    class QueryServiceMock:
        async def create_query(self, session_id: str, user_id: str, question: str) -> Dict[str, Any]:
            return {
                "id": "03084655-d5c4-42b4-b39a-7097f4a5ed1f",
                "session_id": session_id,
                "question": question,
                "answer": "The capital of France is Paris.",
                "bad_answer": False,
                "topic": ["geography", "capital cities"],
                "created_at": "2024-06-01T12:00:00Z",
                "expires_at": "2024-06-01T13:00:00Z",
            }

    return QueryServiceMock()

def get_query_service_create_query_404_mock():
    class QueryServiceMock:
        async def create_query(self, session_id: str, user_id: str, question: str) -> Dict[str, Any]:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    return QueryServiceMock()