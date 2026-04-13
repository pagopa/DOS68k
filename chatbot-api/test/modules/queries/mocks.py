from typing import Any, Dict, List, Optional, Self
from fastapi import HTTPException, status
from dos_utility.database.nosql import NoSQLInterface, KeyCondition, QueryResult, ScanResult

# ---------------------------------------------------------------------------
# Shared imports used by test modules
# ---------------------------------------------------------------------------
__all__ = [
    "MockChatbot",
    "MockQueryRepository",
    "MockQueryRepositoryEmpty",
    "MockSessionRepositoryFound",
    "MockSessionRepositoryNotFound",
    "MOCK_SESSION_ID",
    "MOCK_QUERY_ID",
    "MOCK_USER_ID",
    "get_query_service_get_queries_200_mock",
    "get_query_service_get_queries_404_mock",
    "get_query_service_create_query_201_mock",
    "get_query_service_create_query_404_mock",
]


# ---------------------------------------------------------------------------
# Shared data fixtures
# ---------------------------------------------------------------------------

MOCK_SESSION_ID = "123e4567-e89b-12d3-a456-426614174000"
MOCK_QUERY_ID = "223e4567-e89b-12d3-a456-426614174001"
MOCK_USER_ID = "user-123"

MOCK_SESSION_ITEM = {
    "id": MOCK_SESSION_ID,
    "userId": MOCK_USER_ID,
    "title": "Test Session",
    "createdAt": "2024-01-01T00:00:00",
    "expiresAt": None,
}

MOCK_QUERY_ITEM = {
    "id": MOCK_QUERY_ID,
    "sessionId": MOCK_SESSION_ID,
    "question": "What is Python?",
    "answer": "A programming language",
    "badAnswer": False,
    "topic": ["programming"],
    "createdAt": "2024-01-01T00:00:00",
    "expiresAt": None,
}


class MockNoSQLClientWithQueries(NoSQLInterface):
    async def __aenter__(self: Self) -> Self:
        return self

    async def __aexit__(self: Self, exc_type, exc_val, exc_tb) -> None:
        pass

    async def is_healthy(self: Self) -> bool:
        return True

    async def put_item(self: Self, table_name: str, item: Dict[str, Any]) -> None:
        pass

    async def get_item(self: Self, table_name: str, key: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return None

    async def delete_item(self: Self, table_name: str, key: Dict[str, Any]) -> None:
        pass

    async def update_item(self: Self, table_name: str, key: Dict[str, Any], fields_to_update: Dict[str, Any]) -> None:
        pass

    async def query(self: Self, table_name: str, key_conditions: List[KeyCondition], **kwargs) -> QueryResult:
        return QueryResult(items=[MOCK_QUERY_ITEM], count=1)

    async def scan(self: Self, table_name: str, **kwargs) -> ScanResult:
        return ScanResult(items=[], last_evaluated_key=None)


class MockNoSQLClientEmpty(NoSQLInterface):
    async def __aenter__(self: Self) -> Self:
        return self

    async def __aexit__(self: Self, exc_type, exc_val, exc_tb) -> None:
        pass

    async def is_healthy(self: Self) -> bool:
        return True

    async def put_item(self: Self, table_name: str, item: Dict[str, Any]) -> None:
        pass

    async def get_item(self: Self, table_name: str, key: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return None

    async def delete_item(self: Self, table_name: str, key: Dict[str, Any]) -> None:
        pass

    async def update_item(self: Self, table_name: str, key: Dict[str, Any], fields_to_update: Dict[str, Any]) -> None:
        pass

    async def query(self: Self, table_name: str, key_conditions: List[KeyCondition], **kwargs) -> QueryResult:
        return QueryResult(items=[], count=0)

    async def scan(self: Self, table_name: str, **kwargs) -> ScanResult:
        return ScanResult(items=[], last_evaluated_key=None)


# ---------------------------------------------------------------------------
# Repository mocks (for service tests)
# ---------------------------------------------------------------------------

class MockQueryRepository:
    """Mock for QueryRepository used in QueryService tests."""

    async def get_queries(self: Self, session_id: str) -> List[Dict[str, Any]]:
        return [MOCK_QUERY_ITEM]

    async def create_query(self: Self, session_id: str, query_data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "id": MOCK_QUERY_ID,
            "sessionId": session_id,
            "badAnswer": False,
            "createdAt": "2024-01-01T00:00:00",
            **query_data,
        }

    async def delete_query(self: Self, query_id: str, session_id: str) -> None:
        pass


class MockQueryRepositoryEmpty:
    """Mock for QueryRepository that always returns empty results."""

    async def get_queries(self: Self, session_id: str) -> List[Dict[str, Any]]:
        return []

    async def create_query(self: Self, session_id: str, query_data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "id": MOCK_QUERY_ID,
            "sessionId": session_id,
            "badAnswer": False,
            "createdAt": "2024-01-01T00:00:00",
            **query_data,
        }

    async def delete_query(self: Self, query_id: str, session_id: str) -> None:
        pass


class MockSessionRepositoryFound:
    """Mock for SessionRepository that always finds the session."""

    async def get_session(self: Self, session_id: str, user_id: str) -> Dict[str, Any]:
        return MOCK_SESSION_ITEM

    async def get_sessions(self: Self, user_id: str) -> List[Dict[str, Any]]:
        return [MOCK_SESSION_ITEM]


class MockSessionRepositoryNotFound:
    """Mock for SessionRepository that always returns None."""

    async def get_session(self: Self, session_id: str, user_id: str) -> None:
        return None

    async def get_sessions(self: Self, user_id: str) -> List[Dict[str, Any]]:
        return []


def get_query_service_get_queries_200_mock():
    class QueryServiceMock:
        async def get_queries(self: Self, session_id: str, user_id: str) -> List[Dict[str, Any]]:
            return [
                {
                    "id": "03084655-d5c4-42b4-b39a-7097f4a5ed1f",
                    "session_id": "03084655-d5c4-42b4-b39a-7097f4a5ed1f",
                    "question": "What is the capital of France?",
                    "answer": "The capital of France is Paris.",
                    "bad_answer": False,
                    "topic": ["geography", "capital cities"],
                    "context": {
                        "test.md": [
                            {
                                "chunk_id": 0,
                                "content": "Test content",
                                "score": 0.5,
                            },
                        ],
                    },
                    "created_at": "2024-06-01T12:00:00Z",
                    "expires_at": "2024-06-01T13:00:00Z",
                }
            ]

    return QueryServiceMock()

def get_query_service_get_queries_404_mock():
    class QueryServiceMock:
        async def get_queries(self: Self, session_id: str, user_id: str) -> List[Dict[str, Any]]:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    return QueryServiceMock()

def get_query_service_create_query_201_mock():
    class QueryServiceMock:
        async def create_query(
                self: Self,
                session_id: str,
                user_id: str,
                knowledge_base: Optional[str],
                session_history: Optional[List[Dict[str, str]]],
                question: str,
            ) -> Dict[str, Any]:
            return {
                "id": "03084655-d5c4-42b4-b39a-7097f4a5ed1f",
                "session_id": session_id,
                "question": question,
                "answer": "The capital of France is Paris.",
                "bad_answer": False,
                "topic": ["geography", "capital cities"],
                "context": {
                    "test.md": [
                        {
                            "chunk_id": 0,
                            "content": "Test content",
                            "score": 0.5,
                        },
                    ],
                },
                "created_at": "2024-06-01T12:00:00Z",
                "expires_at": "2024-06-01T13:00:00Z",
            }

    return QueryServiceMock()

def get_query_service_create_query_404_mock():
    class QueryServiceMock:
        async def create_query(
                self: Self,
                session_id: str,
                user_id: str,
                question: str,
                knowledge_base: Optional[str],
                session_history: Optional[List[Dict[str, str]]],
            ) -> Dict[str, Any]:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    return QueryServiceMock()


class MockChatbot:
    """Mock for Chatbot used in QueryService tests."""

    async def chat_generate(
            self: Self,
            query_str: str,
            messages: Optional[List[Dict[str, Any]]] = None,
            knowledge_base: Optional[str] = None,
        ) -> Dict[str, Any]:
        return {
            "response": "Simulated answer",
            "context": {},
        }

class MockMaskingResponse: ...

class MockMaskingResponse200(MockMaskingResponse):
    status_code = 200
    def json(self):
        return "masked text"

class MockMaskingErrorResponse500(MockMaskingResponse):
    status_code = 500
    def json(self):
        return {}

def get_mock_async_client(mock_masking_response: MockMaskingResponse):
    class MockAsyncClient:
        def __init__(self, **kwargs): pass
        async def __aenter__(self): return self
        async def __aexit__(self, *args): pass
        async def post(self, url, json): return mock_masking_response()

    return MockAsyncClient