from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, Dict, List, Optional, Self, Tuple
from dataclasses import dataclass


# ---------------------------------------------------------------------------
# Queue mocks (used by main_test)
# ---------------------------------------------------------------------------


class StopAsyncIteration(Exception):
    pass


class QueueClientMock:
    async def __aenter__(self: Self) -> Self:
        return self

    async def __aexit__(self: Self, exc_type, exc_val, exc_tb) -> None:
        pass

    async def dequeue(self: Self) -> Tuple[Optional[bytes], Optional[str]]:
        return b'{"task": "example"}', "ack_token_example"

    async def acknowledge(self: Self, ack_token: str) -> None:
        pass


class QueueClientLoopMock:
    def __init__(self: Self):
        self._call_count = 0

    async def __aenter__(self: Self) -> Self:
        return self

    async def __aexit__(self: Self, exc_type, exc_val, exc_tb) -> None:
        pass

    async def dequeue(self: Self) -> Tuple[Optional[bytes], Optional[str]]:
        return b'{"task": "example"}', "ack_token_example"

    async def acknowledge(self: Self, ack_token: str) -> None:
        self._call_count += 1

        if self._call_count >= 1:
            raise StopAsyncIteration()


@asynccontextmanager
async def get_queue_client_ctx_mock() -> AsyncGenerator[QueueClientMock, None]:
    async with QueueClientMock() as client:
        yield client


@asynccontextmanager
async def get_queue_client_loop_ctx_mock() -> AsyncGenerator[QueueClientLoopMock, None]:
    async with QueueClientLoopMock() as client:
        yield client


async def process_task_block_loop_mock(body: bytes) -> None:
    raise Exception("Simulated processing error")


async def process_task_noop_mock(body: bytes) -> None:
    return None


# ---------------------------------------------------------------------------
# Task-pipeline mocks (used by task_test)
# ---------------------------------------------------------------------------


MOCK_SESSION_ID = "session-1"
MOCK_QUERY_ID = "query-1"


def make_query_item(
    id: str = MOCK_QUERY_ID,
    session_id: str = MOCK_SESSION_ID,
    question: str = "What is Python?",
    answer: str = "A programming language",
    created_at: str = "2024-01-01T00:00:00",
    context: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    return {
        "id": id,
        "sessionId": session_id,
        "question": question,
        "answer": answer,
        "createdAt": created_at,
        "context": context if context is not None else [{"content": "ctx chunk"}],
        "isEvaluated": False,
    }


@dataclass
class MockTaskSettings:
    provider: str = "google"
    model_id: str = "fake-llm"
    temperature: float = 0.0
    max_tokens: float = 1024.0
    model_api_key: str = "fake-key"
    embed_model_id: str = "fake-embed"
    embed_batch_size: int = 100
    embed_dim: int = 768
    embed_task: str = "RETRIEVAL_DOCUMENT"
    embed_retries: int = 3
    embed_retry_min_seconds: float = 1.0
    config_path: str = "/nonexistent/config.yml"


@dataclass
class MockGlobalSettings:
    log_level: int = 20


@dataclass
class MockNOSQLSettings:
    query_tablename: str = "queries"
    session_tablename: str = "sessions"


class MockQueryResult:
    def __init__(self: Self, items: List[Dict[str, Any]]):
        self.items = items
        self.count = len(items)


class MockNoSQLClient:
    def __init__(self: Self, items: Optional[List[Dict[str, Any]]] = None):
        self.items: List[Dict[str, Any]] = items if items is not None else []
        self.query_calls: List[Dict[str, Any]] = []
        self.update_calls: List[Dict[str, Any]] = []

    async def __aenter__(self: Self) -> Self:
        return self

    async def __aexit__(self: Self, exc_type, exc_val, exc_tb) -> None:
        pass

    async def query(self: Self, table_name: str, key_conditions, **kwargs):
        self.query_calls.append({"table_name": table_name})
        return MockQueryResult(items=self.items)

    async def update_item(
        self: Self,
        table_name: str,
        key: Dict[str, Any],
        fields_to_update: Dict[str, Any],
    ) -> None:
        self.update_calls.append(
            {
                "table_name": table_name,
                "key": key,
                "fields_to_update": fields_to_update,
            }
        )


def make_nosql_client_ctx(client: MockNoSQLClient):
    @asynccontextmanager
    async def _ctx() -> AsyncGenerator[MockNoSQLClient, None]:
        async with client as c:
            yield c

    return _ctx


class MockLLMResponse:
    def __init__(self: Self, text: str):
        self.text = text


class MockLLM:
    def __init__(self: Self, response_text: str = "  contextualized question  "):
        self._response_text = response_text
        self.acomplete_calls: List[Any] = []

    async def acomplete(self: Self, prompt: Any) -> MockLLMResponse:
        self.acomplete_calls.append(prompt)
        return MockLLMResponse(text=self._response_text)


class MockEmbedding:
    pass


class MockEvaluator:
    """Records evaluate() inputs and returns a fixed score dict."""

    _last: Optional["MockEvaluator"] = None

    def __init__(self: Self, settings: Any):
        self.settings = settings
        self.evaluate_calls: List[Dict[str, Any]] = []
        MockEvaluator._last = self

    async def evaluate(
        self: Self, question: str, answer: str, context: List[str]
    ) -> Dict[str, float]:
        self.evaluate_calls.append(
            {"question": question, "answer": answer, "context": context}
        )
        return {"relevancy": 0.9, "faithfulness": 0.8, "utilization": 0.7}


def install_task_mocks(
    monkeypatch,
    nosql_client: MockNoSQLClient,
    llm: Optional[MockLLM] = None,
    task_settings: Optional[MockTaskSettings] = None,
):
    """Patch every external dependency that `task.process_task` touches.

    Returns the (llm, task_settings) used so callers can assert against them.
    """
    from src.worker import task as task_module

    llm = llm if llm is not None else MockLLM()
    task_settings = task_settings if task_settings is not None else MockTaskSettings()
    MockEvaluator._last = None

    monkeypatch.setattr(task_module, "get_task_settings", lambda: task_settings)
    monkeypatch.setattr(
        task_module, "get_global_settings", lambda: MockGlobalSettings()
    )
    monkeypatch.setattr(task_module, "get_nosql_settings", lambda: MockNOSQLSettings())
    monkeypatch.setattr(task_module, "get_llm", lambda **kwargs: llm)
    monkeypatch.setattr(
        task_module, "get_embed_model", lambda **kwargs: MockEmbedding()
    )
    monkeypatch.setattr(task_module, "Evaluator", MockEvaluator)
    monkeypatch.setattr(
        task_module, "get_nosql_client_ctx", make_nosql_client_ctx(nosql_client)
    )

    return llm, task_settings
