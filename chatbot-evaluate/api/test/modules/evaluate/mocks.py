from typing import Any, Dict, List, Optional, Self

from fastapi import HTTPException, status

from dos_utility.database.nosql import (
    NoSQLInterface,
    KeyCondition,
    QueryResult,
    ScanResult,
)


MOCK_USER_ID = "123e4567-e89b-12d3-a456-426614174000"
MOCK_SESSION_ID = "223e4567-e89b-12d3-a456-426614174001"
MOCK_QUERY_ID = "323e4567-e89b-12d3-a456-426614174002"

MOCK_SESSION_ITEM: Dict[str, Any] = {
    "id": MOCK_SESSION_ID,
    "userId": MOCK_USER_ID,
    "title": "Test Session",
    "createdAt": "2024-01-01T00:00:00",
}

MOCK_QUERY_ITEM: Dict[str, Any] = {
    "id": MOCK_QUERY_ID,
    "sessionId": MOCK_SESSION_ID,
    "question": "What is Python?",
    "answer": "A programming language",
    "createdAt": "2024-01-01T00:00:00",
    "feedback": 1,
    "isEvaluated": False,
}


class MockQueueClient:
    def __init__(self: Self) -> None:
        self.enqueued: List[bytes] = []

    async def enqueue(self: Self, msg: bytes) -> str:
        self.enqueued.append(msg)
        return f"msg-{len(self.enqueued)}"

    async def is_healthy(self: Self) -> bool:
        return True


class MockNoSQLClient(NoSQLInterface):
    """Default mock: session is owned, query exists and is not yet evaluated."""

    def __init__(
        self: Self,
        sessions: Optional[List[Dict[str, Any]]] = None,
        queries: Optional[List[Dict[str, Any]]] = None,
        update_returns: Optional[Dict[str, Any]] = None,
    ) -> None:
        self._sessions: List[Dict[str, Any]] = (
            sessions if sessions is not None else [MOCK_SESSION_ITEM]
        )
        self._queries: List[Dict[str, Any]] = (
            queries if queries is not None else [MOCK_QUERY_ITEM]
        )
        self._update_returns: Optional[Dict[str, Any]] = update_returns
        self.update_calls: List[Dict[str, Any]] = []

    async def __aenter__(self: Self) -> Self:
        return self

    async def __aexit__(self: Self, exc_type, exc_val, exc_tb) -> None:
        pass

    async def is_healthy(self: Self) -> bool:
        return True

    async def put_item(self: Self, table_name: str, item: Dict[str, Any]) -> None:
        pass

    async def get_item(
        self: Self, table_name: str, key: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        return None

    async def delete_item(self: Self, table_name: str, key: Dict[str, Any]) -> None:
        pass

    async def update_item(
        self: Self,
        table_name: str,
        key: Dict[str, Any],
        fields_to_update: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        self.update_calls.append(
            {"table": table_name, "key": key, "fields": fields_to_update}
        )
        if self._update_returns is None:
            return None
        return {**self._update_returns, **fields_to_update}

    async def query(
        self: Self, table_name: str, key_conditions: List[KeyCondition], **kwargs
    ) -> QueryResult:
        if table_name.endswith("sessions") or "session" in table_name.lower():
            items = self._sessions
        else:
            items = self._queries
        return QueryResult(items=items, count=len(items))

    async def scan(self: Self, table_name: str, **kwargs) -> ScanResult:
        return ScanResult(items=[], last_evaluated_key=None)


# ---------------------------------------------------------------------------
# Controller dependency mocks
# ---------------------------------------------------------------------------


def get_evaluation_service_simple_feedback_201_mock():
    class EvaluationServiceMock:
        async def create_simple_feedback(
            self: Self,
            user_id: str,
            session_id,
            query_id,
            feedback: int,
        ) -> Dict[str, Any]:
            return {
                "id": str(query_id),
                "sessionId": str(session_id),
                "feedback": feedback == 1,
            }

    return EvaluationServiceMock()


def get_evaluation_service_simple_feedback_404_mock():
    class EvaluationServiceMock:
        async def create_simple_feedback(
            self: Self,
            user_id: str,
            session_id,
            query_id,
            feedback: int,
        ) -> Dict[str, Any]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found",
            )

    return EvaluationServiceMock()


def get_evaluation_service_evaluate_201_mock():
    class EvaluationServiceMock:
        async def evaluate(self: Self, query_id, session_id) -> Dict[str, Any]:
            return {
                "queryId": str(query_id),
                "sessionId": str(session_id),
                "status": "queued",
            }

    return EvaluationServiceMock()


def get_evaluation_service_evaluate_404_mock():
    class EvaluationServiceMock:
        async def evaluate(self: Self, query_id, session_id) -> Dict[str, Any]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Query not found",
            )

    return EvaluationServiceMock()


def get_evaluation_service_evaluate_all_201_mock():
    class EvaluationServiceMock:
        async def evaluate_all(self: Self, session_id) -> Dict[str, Any]:
            return {
                "evaluations": [
                    {
                        "queryId": MOCK_QUERY_ID,
                        "sessionId": str(session_id),
                        "status": "queued",
                    }
                ]
            }

    return EvaluationServiceMock()
