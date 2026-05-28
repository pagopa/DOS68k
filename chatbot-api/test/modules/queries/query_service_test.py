import pytest

from typing import Any, Dict

from fastapi import HTTPException

from src.modules.queries.service import QueryService, get_query_service
from src.modules.env import get_masking_settings
from src.modules.sessions.env import get_session_settings

from test.modules.queries.mocks import (
    MockQueryRepository,
    MockQueryRepositoryEmpty,
    MockSessionRepositoryFound,
    MockSessionRepositoryNotFound,
    MockChatbot,
    MockTracer,
    MockTracerThatRaises,
    MockMaskingResponse200,
    MockMaskingErrorResponse500,
    MOCK_SESSION_ID,
    MOCK_QUERY_ID,
    MOCK_TRACE_ID,
    get_mock_async_client,
)


@pytest.fixture(autouse=True)
def setup_env(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("SESSION_EXPIRATION_DAYS", "30")
    monkeypatch.setenv("MASK_PII", "false")
    get_session_settings.cache_clear()
    get_masking_settings.cache_clear()


# ---------------------------------------------------------------------------
# get_queries
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_queries_returns_list():
    service = QueryService(
        query_repository=MockQueryRepository(),
        session_repository=MockSessionRepositoryFound(),
        chatbot=MockChatbot(),
        tracer=MockTracer(),
    )
    result = await service.get_queries(session_id=MOCK_SESSION_ID, user_id="user-123")

    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0]["id"] == MOCK_QUERY_ID
    assert result[0]["session_id"] == MOCK_SESSION_ID
    assert result[0]["question"] == "What is Python?"
    assert result[0]["feedback"] == 0


@pytest.mark.asyncio
async def test_get_queries_session_not_found():
    service = QueryService(
        query_repository=MockQueryRepository(),
        session_repository=MockSessionRepositoryNotFound(),
        chatbot=MockChatbot(),
        tracer=MockTracer(),
    )

    with pytest.raises(HTTPException) as exc_info:
        await service.get_queries(session_id=MOCK_SESSION_ID, user_id="user-123")

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Session not found"


@pytest.mark.asyncio
async def test_get_queries_empty_when_no_queries():
    service = QueryService(
        query_repository=MockQueryRepositoryEmpty(),
        session_repository=MockSessionRepositoryFound(),
        chatbot=MockChatbot(),
        tracer=MockTracer(),
    )
    result = await service.get_queries(session_id=MOCK_SESSION_ID, user_id="user-123")

    assert result == []


# ---------------------------------------------------------------------------
# create_query
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_query_success():
    service = QueryService(
        query_repository=MockQueryRepository(),
        session_repository=MockSessionRepositoryFound(),
        chatbot=MockChatbot(),
        tracer=MockTracer(),
    )
    result = await service.create_query(
        session_id=MOCK_SESSION_ID,
        user_id="user-123",
        user_role="user",
        question="What is Python?",
        session_history=None,
    )

    assert "id" in result
    assert result["session_id"] == MOCK_SESSION_ID
    assert result["question"] == "What is Python?"
    assert result["answer"] == "Simulated answer"
    assert result["feedback"] == 0
    assert "created_at" in result


@pytest.mark.asyncio
async def test_create_query_sanitizes_html():
    service = QueryService(
        query_repository=MockQueryRepository(),
        session_repository=MockSessionRepositoryFound(),
        chatbot=MockChatbot(),
        tracer=MockTracer(),
    )
    result = await service.create_query(
        session_id=MOCK_SESSION_ID,
        user_id="user-123",
        user_role="user",
        question="<script>alert('xss')</script>Clean question",
        session_history=None,
    )

    # nh3 strips script tags
    assert "<script>" not in result["question"]
    assert "Clean question" in result["question"]


@pytest.mark.asyncio
async def test_create_query_session_not_found():
    service = QueryService(
        query_repository=MockQueryRepository(),
        session_repository=MockSessionRepositoryNotFound(),
        chatbot=MockChatbot(),
        tracer=MockTracer(),
    )

    with pytest.raises(HTTPException) as exc_info:
        await service.create_query(
            session_id=MOCK_SESSION_ID,
            user_id="user-123",
            user_role="user",
            question="What is Python?",
            session_history=None,
        )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Session not found"


# ---------------------------------------------------------------------------
# create_query — PII masking
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_query_masks_question_and_answer_when_pii_enabled(
    monkeypatch: pytest.MonkeyPatch,
):
    get_masking_settings.cache_clear()

    monkeypatch.setenv("MASK_PII", "true")
    monkeypatch.setattr(
        "src.modules.queries.service.AsyncClient",
        get_mock_async_client(MockMaskingResponse200),
    )

    service = QueryService(
        query_repository=MockQueryRepository(),
        session_repository=MockSessionRepositoryFound(),
        chatbot=MockChatbot(),
        tracer=MockTracer(),
    )
    result = await service.create_query(
        session_id=MOCK_SESSION_ID,
        user_id="user-123",
        user_role="user",
        question="What is Python?",
        session_history=None,
    )

    assert result["question"] == "masked text"
    assert result["answer"] == "masked text"


@pytest.mark.asyncio
async def test_create_query_raises_500_when_masking_service_fails(
    monkeypatch: pytest.MonkeyPatch,
):
    get_masking_settings.cache_clear()

    monkeypatch.setenv("MASK_PII", "true")
    monkeypatch.setattr(
        "src.modules.queries.service.AsyncClient",
        get_mock_async_client(MockMaskingErrorResponse500),
    )

    service = QueryService(
        query_repository=MockQueryRepository(),
        session_repository=MockSessionRepositoryFound(),
        chatbot=MockChatbot(),
        tracer=MockTracer(),
    )

    with pytest.raises(HTTPException) as exc_info:
        await service.create_query(
            session_id=MOCK_SESSION_ID,
            user_id="user-123",
            user_role="user",
            question="What is Python?",
            session_history=None,
        )

    assert exc_info.value.status_code == 500
    assert exc_info.value.detail == "Masking service error"


# ---------------------------------------------------------------------------
# get_query_service
# ---------------------------------------------------------------------------


def test_get_query_service_returns_instance():
    service = get_query_service(
        query_repository=MockQueryRepository(),
        session_repository=MockSessionRepositoryFound(),
        chatbot=MockChatbot(),
        tracer=MockTracer(),
    )

    assert isinstance(service, QueryService)


# ---------------------------------------------------------------------------
# create_query — tracing
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_query_calls_tracer_once():
    tracer = MockTracer()
    service = QueryService(
        query_repository=MockQueryRepository(),
        session_repository=MockSessionRepositoryFound(),
        chatbot=MockChatbot(),
        tracer=tracer,
    )
    await service.create_query(
        session_id=MOCK_SESSION_ID,
        user_id="user-123",
        user_role="user",
        question="What is Python?",
        session_history=None,
    )

    assert tracer.trace_call_count == 1


@pytest.mark.asyncio
async def test_create_query_persists_tracing_trace_id():
    captured_query_data = {}

    class CapturingQueryRepository(MockQueryRepository):
        async def create_query(self, session_id: str, query_data):
            captured_query_data.update(query_data)
            return await super().create_query(
                session_id=session_id, query_data=query_data
            )

    service = QueryService(
        query_repository=CapturingQueryRepository(),
        session_repository=MockSessionRepositoryFound(),
        chatbot=MockChatbot(),
        tracer=MockTracer(),
    )
    result = await service.create_query(
        session_id=MOCK_SESSION_ID,
        user_id="user-123",
        user_role="user",
        question="What is Python?",
        session_history=None,
    )

    assert captured_query_data.get("tracingTraceId") == MOCK_TRACE_ID
    assert result["tracing_trace_id"] == MOCK_TRACE_ID


@pytest.mark.asyncio
async def test_create_query_succeeds_when_tracer_raises():
    service = QueryService(
        query_repository=MockQueryRepository(),
        session_repository=MockSessionRepositoryFound(),
        chatbot=MockChatbot(),
        tracer=MockTracerThatRaises(),
    )
    result = await service.create_query(
        session_id=MOCK_SESSION_ID,
        user_id="user-123",
        user_role="user",
        question="What is Python?",
        session_history=None,
    )

    assert "answer" in result
    assert result.get("tracing_trace_id") is None


@pytest.mark.asyncio
async def test_create_query_opens_outer_spans_without_masking():
    tracer = MockTracer()
    service = QueryService(
        query_repository=MockQueryRepository(),
        session_repository=MockSessionRepositoryFound(),
        chatbot=MockChatbot(),
        tracer=tracer,
    )
    await service.create_query(
        session_id=MOCK_SESSION_ID,
        user_id="user-123",
        user_role="user",
        question="What is Python?",
        session_history=None,
    )

    assert tracer.span_names == ["sanitize_input", "load_history"]


@pytest.mark.asyncio
async def test_create_query_opens_outer_spans_with_masking(
    monkeypatch: pytest.MonkeyPatch,
):
    get_masking_settings.cache_clear()
    monkeypatch.setenv("MASK_PII", "true")
    monkeypatch.setattr(
        "src.modules.queries.service.AsyncClient",
        get_mock_async_client(MockMaskingResponse200),
    )

    tracer = MockTracer()
    service = QueryService(
        query_repository=MockQueryRepository(),
        session_repository=MockSessionRepositoryFound(),
        chatbot=MockChatbot(),
        tracer=tracer,
    )
    await service.create_query(
        session_id=MOCK_SESSION_ID,
        user_id="user-123",
        user_role="user",
        question="What is Python?",
        session_history=None,
    )

    assert tracer.span_names == [
        "sanitize_input",
        "load_history",
        "mask_pii_input",
        "mask_pii_output",
    ]


@pytest.mark.asyncio
async def test_create_query_assembles_trace_metadata_no_masking_user_role():
    """Without masking, a real LLM response, and a 'user' role:
    masking.enabled=False, masking.*_changed absent, response.fallback=False,
    user.role='user', and build/config hashes present."""
    tracer = MockTracer()
    service = QueryService(
        query_repository=MockQueryRepository(),
        session_repository=MockSessionRepositoryFound(),
        chatbot=MockChatbot(),
        tracer=tracer,
    )
    await service.create_query(
        session_id=MOCK_SESSION_ID,
        user_id="user-123",
        user_role="user",
        question="What is Python?",
        session_history=None,
    )

    merged: Dict[str, Any] = {}
    for call in tracer.metadata_calls:
        merged.update(call)

    assert merged["masking.enabled"] is False
    assert "masking.input_changed" not in merged
    assert "masking.output_changed" not in merged
    assert merged["user.role"] == "user"
    assert merged["response.fallback"] is False
    assert merged["chatbot_api.version"]  # non-empty
    assert len(merged["agent.config_hash"]) == 12
    assert len(merged["tool.config_hash"]) == 12


@pytest.mark.asyncio
async def test_create_query_metadata_marks_fallback_when_chatbot_returns_canned_string():
    from src.modules.chatbot.chatbot import FALLBACK_RESPONSE

    tracer = MockTracer()
    service = QueryService(
        query_repository=MockQueryRepository(),
        session_repository=MockSessionRepositoryFound(),
        chatbot=MockChatbot(response=FALLBACK_RESPONSE),
        tracer=tracer,
    )
    await service.create_query(
        session_id=MOCK_SESSION_ID,
        user_id="user-123",
        user_role="admin",
        question="What is Python?",
        session_history=None,
    )

    merged: Dict[str, Any] = {}
    for call in tracer.metadata_calls:
        merged.update(call)

    assert merged["response.fallback"] is True
    assert merged["user.role"] == "admin"


@pytest.mark.asyncio
async def test_create_query_metadata_includes_masking_flags_when_enabled(
    monkeypatch: pytest.MonkeyPatch,
):
    get_masking_settings.cache_clear()
    monkeypatch.setenv("MASK_PII", "true")
    monkeypatch.setattr(
        "src.modules.queries.service.AsyncClient",
        get_mock_async_client(MockMaskingResponse200),
    )

    tracer = MockTracer()
    service = QueryService(
        query_repository=MockQueryRepository(),
        session_repository=MockSessionRepositoryFound(),
        chatbot=MockChatbot(),
        tracer=tracer,
    )
    await service.create_query(
        session_id=MOCK_SESSION_ID,
        user_id="user-123",
        user_role="user",
        question="What is Python?",
        session_history=None,
    )

    merged: Dict[str, Any] = {}
    for call in tracer.metadata_calls:
        merged.update(call)

    assert merged["masking.enabled"] is True
    # Mock masking changes both input and output to "masked text".
    assert merged["masking.input_changed"] is True
    assert merged["masking.output_changed"] is True


@pytest.mark.asyncio
async def test_create_query_invokes_chat_generate_once_under_tracing_fault():
    """Regression: tracing faults must not double the LLM call."""
    chatbot = MockChatbot()
    service = QueryService(
        query_repository=MockQueryRepository(),
        session_repository=MockSessionRepositoryFound(),
        chatbot=chatbot,
        tracer=MockTracerThatRaises(),
    )
    await service.create_query(
        session_id=MOCK_SESSION_ID,
        user_id="user-123",
        user_role="user",
        question="What is Python?",
        session_history=None,
    )

    assert chatbot.chat_generate_call_count == 1
