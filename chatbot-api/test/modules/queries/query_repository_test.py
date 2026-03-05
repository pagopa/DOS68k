import pytest

from src.modules.queries.repository import QueryRepository
from src.modules.env import get_session_settings

from test.modules.queries.mocks import (
    MockNoSQLClientWithQueries,
    MockNoSQLClientEmpty,
    MOCK_SESSION_ID,
    MOCK_QUERY_ID,
)


@pytest.fixture(autouse=True)
def setup_env(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("SESSION_EXPIRATION_DAYS", "30")
    get_session_settings.cache_clear()


# ---------------------------------------------------------------------------
# get_queries
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_get_queries_returns_items():
    repo = QueryRepository(nosql_client=MockNoSQLClientWithQueries())
    result = await repo.get_queries(session_id=MOCK_SESSION_ID)

    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0]["id"] == MOCK_QUERY_ID
    assert result[0]["sessionId"] == MOCK_SESSION_ID


@pytest.mark.asyncio
async def test_get_queries_returns_empty():
    repo = QueryRepository(nosql_client=MockNoSQLClientEmpty())
    result = await repo.get_queries(session_id=MOCK_SESSION_ID)

    assert result == []


# ---------------------------------------------------------------------------
# create_query
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_create_query_returns_item():
    repo = QueryRepository(nosql_client=MockNoSQLClientEmpty())
    result = await repo.create_query(
        session_id=MOCK_SESSION_ID,
        query_data={
            "question": "What is Python?",
            "answer": "A programming language",
            "expiresAt": None,
            "topic": ["programming"],
        },
    )

    assert "id" in result
    assert result["sessionId"] == MOCK_SESSION_ID
    assert result["question"] == "What is Python?"
    assert result["answer"] == "A programming language"
    assert result["badAnswer"] is False
    assert result["topic"] == ["programming"]
    assert "createdAt" in result


@pytest.mark.asyncio
async def test_create_query_generates_unique_id():
    repo = QueryRepository(nosql_client=MockNoSQLClientEmpty())
    result_1 = await repo.create_query(
        session_id=MOCK_SESSION_ID,
        query_data={"question": "Q1", "answer": "A1", "expiresAt": None, "topic": []},
    )
    result_2 = await repo.create_query(
        session_id=MOCK_SESSION_ID,
        query_data={"question": "Q2", "answer": "A2", "expiresAt": None, "topic": []},
    )

    assert result_1["id"] != result_2["id"]


# ---------------------------------------------------------------------------
# delete_query
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_delete_query_does_not_raise():
    repo = QueryRepository(nosql_client=MockNoSQLClientEmpty())

    # Should complete without raising any exception
    await repo.delete_query(query_id=MOCK_QUERY_ID, session_id=MOCK_SESSION_ID)
