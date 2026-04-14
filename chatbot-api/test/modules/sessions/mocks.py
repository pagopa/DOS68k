from typing import Any, Dict, List, Optional, Self
from fastapi import HTTPException, status
from dos_utility.database.nosql import NoSQLInterface, KeyCondition, QueryResult, ScanResult


# ---------------------------------------------------------------------------
# Shared data fixtures
# ---------------------------------------------------------------------------

MOCK_SESSION_ID = "123e4567-e89b-12d3-a456-426614174000"
MOCK_USER_ID = "user-123"
MOCK_QUERY_ID = "223e4567-e89b-12d3-a456-426614174001"

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


# ---------------------------------------------------------------------------
# NoSQL client mocks (for repository tests)
# ---------------------------------------------------------------------------

class MockNoSQLClientWithSession(NoSQLInterface):
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
        return QueryResult(items=[MOCK_SESSION_ITEM], count=1)

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

class MockSessionRepository:
    """Mock for SessionRepository that always finds the session."""

    async def get_session(self: Self, session_id: str, user_id: str) -> Dict[str, Any]:
        return MOCK_SESSION_ITEM

    async def get_sessions(self: Self, user_id: str) -> List[Dict[str, Any]]:
        return [MOCK_SESSION_ITEM]

    async def create_session(self: Self, user_id: str, session_data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "id": MOCK_SESSION_ID,
            "userId": user_id,
            "createdAt": "2024-01-01T00:00:00",
            **session_data,
        }

    async def delete_session(self: Self, session_id: str, user_id: str) -> None:
        pass


class MockSessionRepositoryNotFound:
    """Mock for SessionRepository that always returns None."""

    async def get_session(self: Self, session_id: str, user_id: str) -> None:
        return None

    async def get_sessions(self: Self, user_id: str) -> List[Dict[str, Any]]:
        return []

    async def create_session(self: Self, user_id: str, session_data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "id": MOCK_SESSION_ID,
            "userId": user_id,
            "createdAt": "2024-01-01T00:00:00",
            **session_data,
        }

    async def delete_session(self: Self, session_id: str, user_id: str) -> None:
        pass


class MockQueryRepository:
    """Mock for QueryRepository used in SessionService tests."""

    async def get_queries(self: Self, session_id: str) -> List[Dict[str, Any]]:
        return [MOCK_QUERY_ITEM]

    async def delete_query(self: Self, query_id: str, session_id: str) -> None:
        pass


class MockQueryRepositoryEmpty:
    """Mock for QueryRepository that always returns empty results."""

    async def get_queries(self: Self, session_id: str) -> List[Dict[str, Any]]:
        return []

    async def delete_query(self: Self, query_id: str, session_id: str) -> None:
        pass


# ---------------------------------------------------------------------------
# Service mocks (for controller tests)
# ---------------------------------------------------------------------------

def get_session_service_get_sessions_mock():
    class SessionServiceMock:
        async def get_sessions(self, user_id: str):
            return [
                {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "user_id": user_id,
                    "title": "Session 1",
                    "created_at": "2024-01-01T00:00:00Z",
                    "updated_at": "2024-01-01T00:00:00Z",
                    "expires_at": "2024-01-02T00:00:00Z",
                },
                {
                    "id": "123e4567-e89b-12d3-a456-426614174001",
                    "user_id": user_id,
                    "title": "Session 2",
                    "created_at": "2024-01-02T00:00:00Z",
                    "updated_at": "2024-01-02T00:00:00Z",
                    "expires_at": "2024-01-02T00:00:00Z",
                },
            ]

    return SessionServiceMock()

def get_session_service_get_session_200_mock():
    class SessionServiceMock:
        async def get_session(self, session_id: str, user_id: str):
            return {
                "id": session_id,
                "user_id": user_id,
                "title": "Session 1",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
                    "expires_at": "2024-01-02T00:00:00Z",
            }

    return SessionServiceMock()

def get_session_service_get_session_404_mock():
    class SessionServiceMock:
        async def get_session(self, session_id: str, user_id: str):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    return SessionServiceMock()

def get_session_service_create_session_mock():
    class SessionServiceMock:
        async def create_session(self, user_id: str, session_data: dict, is_temporary: bool):
            return {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "user_id": user_id,
                "title": session_data["title"],
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
                "expires_at": "2024-01-02T00:00:00Z",
            }

    return SessionServiceMock()

def get_session_service_delete_session_204_mock():
    class SessionServiceMock:
        async def delete_session(self, session_id: str, user_id: str):
            return

    return SessionServiceMock()

def get_session_service_delete_session_404_mock():
    class SessionServiceMock:
        async def delete_session(self, session_id: str, user_id: str):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    return SessionServiceMock()

def get_session_service_clear_session_mock():
    class SessionServiceMock:
        async def clear_session(self: Self, session_id: str, user_id: str):
            return {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "title": "Session 1",
                "created_at": "2024-01-01T00:00:00Z",
                "expires_at": None,
            }

    return SessionServiceMock()