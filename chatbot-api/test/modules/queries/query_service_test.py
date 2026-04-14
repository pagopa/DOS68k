import pytest

from fastapi import HTTPException

from src.modules.queries.service import QueryService, get_query_service
from src.modules.env import get_session_settings, get_masking_settings

from test.modules.queries.mocks import (
    MockQueryRepository,
    MockQueryRepositoryEmpty,
    MockSessionRepositoryFound,
    MockSessionRepositoryNotFound,
    MockChatbot,
    MockMaskingResponse200,
    MockMaskingErrorResponse500,
    MOCK_SESSION_ID,
    MOCK_QUERY_ID,
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
    )
    result = await service.get_queries(session_id=MOCK_SESSION_ID, user_id="user-123")

    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0]["id"] == MOCK_QUERY_ID
    assert result[0]["session_id"] == MOCK_SESSION_ID
    assert result[0]["question"] == "What is Python?"
    assert result[0]["bad_answer"] is False


@pytest.mark.asyncio
async def test_get_queries_session_not_found():
    service = QueryService(
        query_repository=MockQueryRepository(),
        session_repository=MockSessionRepositoryNotFound(),
        chatbot=MockChatbot(),
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
    )
    result = await service.create_query(
        session_id=MOCK_SESSION_ID,
        user_id="user-123",
        question="What is Python?",
        session_history=None,
    )

    assert "id" in result
    assert result["session_id"] == MOCK_SESSION_ID
    assert result["question"] == "What is Python?"
    assert result["answer"] == "Simulated answer"
    assert result["bad_answer"] is False
    assert "created_at" in result


@pytest.mark.asyncio
async def test_create_query_sanitizes_html():
    service = QueryService(
        query_repository=MockQueryRepository(),
        session_repository=MockSessionRepositoryFound(),
        chatbot=MockChatbot(),
    )
    result = await service.create_query(
        session_id=MOCK_SESSION_ID,
        user_id="user-123",
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
    )

    with pytest.raises(HTTPException) as exc_info:
        await service.create_query(
            session_id=MOCK_SESSION_ID,
            user_id="user-123",
            question="What is Python?",
            session_history=None,
        )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Session not found"


# ---------------------------------------------------------------------------
# create_query — PII masking
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_create_query_masks_question_and_answer_when_pii_enabled(monkeypatch: pytest.MonkeyPatch):
    get_masking_settings.cache_clear()

    monkeypatch.setenv("MASK_PII", "true")
    monkeypatch.setattr("src.modules.queries.service.AsyncClient", get_mock_async_client(MockMaskingResponse200))

    service = QueryService(
        query_repository=MockQueryRepository(),
        session_repository=MockSessionRepositoryFound(),
        chatbot=MockChatbot(),
    )
    result = await service.create_query(
        session_id=MOCK_SESSION_ID,
        user_id="user-123",
        question="What is Python?",
        session_history=None,
    )

    assert result["question"] == "masked text"
    assert result["answer"] == "masked text"


@pytest.mark.asyncio
async def test_create_query_raises_500_when_masking_service_fails(monkeypatch: pytest.MonkeyPatch):
    get_masking_settings.cache_clear()

    monkeypatch.setenv("MASK_PII", "true")
    monkeypatch.setattr("src.modules.queries.service.AsyncClient", get_mock_async_client(MockMaskingErrorResponse500))

    service = QueryService(
        query_repository=MockQueryRepository(),
        session_repository=MockSessionRepositoryFound(),
        chatbot=MockChatbot(),
    )

    with pytest.raises(HTTPException) as exc_info:
        await service.create_query(
            session_id=MOCK_SESSION_ID,
            user_id="user-123",
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
    )

    assert isinstance(service, QueryService)
