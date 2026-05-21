from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional, Self

from fastapi import HTTPException, status
from dos_utility.database.nosql import (
    NoSQLInterface,
    KeyCondition,
    QueryResult,
    ScanResult,
)
from dos_utility.tracing.interface import TracingInterface, TraceHandle, SpanHandle
from dos_utility.tracing.models import TraceId

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
    "topic": ["programming"],
    "context": [],
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
    ) -> None:
        pass

    async def query(
        self: Self, table_name: str, key_conditions: List[KeyCondition], **kwargs
    ) -> QueryResult:
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
    ) -> None:
        pass

    async def query(
        self: Self, table_name: str, key_conditions: List[KeyCondition], **kwargs
    ) -> QueryResult:
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

    async def create_query(
        self: Self, session_id: str, query_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        return {
            "id": MOCK_QUERY_ID,
            "sessionId": session_id,
            "createdAt": "2024-01-01T00:00:00",
            **query_data,
        }

    async def delete_query(self: Self, query_id: str, session_id: str) -> None:
        pass


class MockQueryRepositoryEmpty:
    """Mock for QueryRepository that always returns empty results."""

    async def get_queries(self: Self, session_id: str) -> List[Dict[str, Any]]:
        return []

    async def create_query(
        self: Self, session_id: str, query_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        return {
            "id": MOCK_QUERY_ID,
            "sessionId": session_id,
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
        async def get_queries(
            self: Self, session_id: str, user_id: str
        ) -> List[Dict[str, Any]]:
            return [
                {
                    "id": "03084655-d5c4-42b4-b39a-7097f4a5ed1f",
                    "session_id": "03084655-d5c4-42b4-b39a-7097f4a5ed1f",
                    "question": "What is the capital of France?",
                    "answer": "The capital of France is Paris.",
                    "bad_answer": False,
                    "topic": ["geography", "capital cities"],
                    "context": [
                        {
                            "chunk_id": 0,
                            "content": "Test content",
                            "score": 0.5,
                            "filename": "test.md",
                        }
                    ],
                    "created_at": "2024-06-01T12:00:00Z",
                    "expires_at": "2024-06-01T13:00:00Z",
                }
            ]

    return QueryServiceMock()


def get_query_service_get_queries_404_mock():
    class QueryServiceMock:
        async def get_queries(
            self: Self, session_id: str, user_id: str
        ) -> List[Dict[str, Any]]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Session not found"
            )

    return QueryServiceMock()


def get_query_service_create_query_201_mock():
    class QueryServiceMock:
        async def create_query(
            self: Self,
            session_id: str,
            user_id: str,
            user_role: str,
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
                "context": [
                    {
                        "chunk_id": 0,
                        "content": "Test content",
                        "score": 0.5,
                        "filename": "test.md",
                    }
                ],
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
            user_role: str,
            question: str,
            session_history: Optional[List[Dict[str, str]]],
        ) -> Dict[str, Any]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Session not found"
            )

    return QueryServiceMock()


class MockChatbot:
    """Mock for Chatbot used in QueryService tests."""

    def __init__(self, response: str = "Simulated answer") -> None:
        self.chat_generate_call_count = 0
        self._response = response

    async def chat_generate(
        self: Self,
        query_str: str,
        messages: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        self.chat_generate_call_count += 1
        return {
            "response": self._response,
            "context": {},
        }


MOCK_TRACE_ID = "mock-trace-id-1234"


class _MockSpanHandle(SpanHandle):
    def set_output(self, output: str) -> None:
        pass

    def set_metadata(self, metadata: Dict[str, Any]) -> None:
        pass


class _MockTraceHandle(TraceHandle):
    def __init__(
        self,
        trace_id: Optional[str] = MOCK_TRACE_ID,
        span_names: Optional[List[str]] = None,
        metadata_calls: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        self._trace_id = trace_id
        self.span_names: List[str] = span_names if span_names is not None else []
        self.metadata_calls: List[Dict[str, Any]] = (
            metadata_calls if metadata_calls is not None else []
        )

    @property
    def id(self) -> TraceId:
        return self._trace_id

    def start_span(self, name: str, input=None, metadata=None):
        names = self.span_names

        @asynccontextmanager
        async def _ctx():
            names.append(name)
            yield _MockSpanHandle()

        return _ctx()

    def set_output(self, output: str) -> None:
        pass

    def set_metadata(self, metadata: Dict[str, Any]) -> None:
        self.metadata_calls.append(dict(metadata))


class MockTracer(TracingInterface):
    """Recording mock tracer for service tests."""

    def __init__(self) -> None:
        self.trace_call_count = 0
        self.span_names: List[str] = []
        self.metadata_calls: List[Dict[str, Any]] = []

    async def __aenter__(self: Self) -> Self:
        return self

    async def __aexit__(self: Self, exc_type, exc_val, exc_tb) -> None:
        pass

    async def is_healthy(self: Self) -> bool:
        return True

    def trace(
        self: Self,
        name: str,
        session_id=None,
        user_id=None,
        input=None,
        metadata=None,
        tags=None,
    ):
        tracer = self

        @asynccontextmanager
        async def _ctx():
            tracer.trace_call_count += 1
            yield _MockTraceHandle(
                span_names=tracer.span_names,
                metadata_calls=tracer.metadata_calls,
            )

        return _ctx()

    async def score(
        self: Self, trace_id: TraceId, name: str, value: float, comment=None
    ) -> None:
        pass

    async def flush(self: Self, timeout=None) -> None:
        pass


class MockTracerThatRaises(TracingInterface):
    """Non-fatal tracer whose SDK calls fail: trace opens, body runs, id is None.

    Models the contractual behaviour of a real provider when the backend is
    unreachable — every operation is swallowed-and-logged internally and the
    request path proceeds normally.
    """

    async def __aenter__(self: Self) -> Self:
        return self

    async def __aexit__(self: Self, exc_type, exc_val, exc_tb) -> None:
        pass

    async def is_healthy(self: Self) -> bool:
        return False

    def trace(
        self: Self,
        name: str,
        session_id=None,
        user_id=None,
        input=None,
        metadata=None,
        tags=None,
    ):
        @asynccontextmanager
        async def _ctx():
            yield _MockTraceHandle(trace_id=None)

        return _ctx()

    async def score(
        self: Self, trace_id: TraceId, name: str, value: float, comment=None
    ) -> None:
        pass

    async def flush(self: Self, timeout=None) -> None:
        pass


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
        def __init__(self, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            pass

        async def post(self, url, json):
            return mock_masking_response()

    return MockAsyncClient
