import pytest

from fastapi import HTTPException

from src.modules.queries.service import QueryService
from src.modules.env import get_session_settings, get_masking_settings

from test.modules.queries.mocks import (
    MockQueryRepository,
    MockQueryRepositoryEmpty,
    MockSessionRepositoryFound,
    MockSessionRepositoryNotFound,
    MockChatbot,
    MOCK_SESSION_ID,
    MOCK_QUERY_ID,
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
        )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Session not found"
