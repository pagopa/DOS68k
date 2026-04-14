import pytest

from src.modules.sessions.repository import SessionRepository, get_session_repository

from test.modules.sessions.mocks import (
    MockNoSQLClientWithSession,
    MockNoSQLClientEmpty,
    MOCK_SESSION_ID,
    MOCK_USER_ID,
)


# ---------------------------------------------------------------------------
# get_session
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_get_session_found():
    repo = SessionRepository(nosql_client=MockNoSQLClientWithSession())
    result = await repo.get_session(session_id=MOCK_SESSION_ID, user_id=MOCK_USER_ID)

    assert result is not None
    assert result["id"] == MOCK_SESSION_ID
    assert result["userId"] == MOCK_USER_ID


@pytest.mark.asyncio
async def test_get_session_not_found():
    repo = SessionRepository(nosql_client=MockNoSQLClientEmpty())
    result = await repo.get_session(session_id=MOCK_SESSION_ID, user_id=MOCK_USER_ID)

    assert result is None


# ---------------------------------------------------------------------------
# get_sessions
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_get_sessions_returns_list():
    repo = SessionRepository(nosql_client=MockNoSQLClientWithSession())
    result = await repo.get_sessions(user_id=MOCK_USER_ID)

    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0]["userId"] == MOCK_USER_ID


@pytest.mark.asyncio
async def test_get_sessions_returns_empty():
    repo = SessionRepository(nosql_client=MockNoSQLClientEmpty())
    result = await repo.get_sessions(user_id=MOCK_USER_ID)

    assert result == []


# ---------------------------------------------------------------------------
# create_session
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_create_session_returns_item():
    repo = SessionRepository(nosql_client=MockNoSQLClientEmpty())
    result = await repo.create_session(
        user_id=MOCK_USER_ID,
        session_data={"title": "New Session", "expiresAt": None},
    )

    assert "id" in result
    assert result["userId"] == MOCK_USER_ID
    assert result["title"] == "New Session"
    assert result["expiresAt"] is None
    assert "createdAt" in result


@pytest.mark.asyncio
async def test_create_session_generates_unique_id():
    repo = SessionRepository(nosql_client=MockNoSQLClientEmpty())
    result_1 = await repo.create_session(
        user_id=MOCK_USER_ID,
        session_data={"title": "Session A", "expiresAt": None},
    )
    result_2 = await repo.create_session(
        user_id=MOCK_USER_ID,
        session_data={"title": "Session B", "expiresAt": None},
    )

    assert result_1["id"] != result_2["id"]


# ---------------------------------------------------------------------------
# delete_session
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_delete_session_does_not_raise():
    repo = SessionRepository(nosql_client=MockNoSQLClientEmpty())

    # Should complete without raising any exception
    await repo.delete_session(session_id=MOCK_SESSION_ID, user_id=MOCK_USER_ID)


# ---------------------------------------------------------------------------
# get_session_repository
# ---------------------------------------------------------------------------

def test_get_session_repository_returns_instance():
    repo = get_session_repository(nosql_client=MockNoSQLClientEmpty())

    assert isinstance(repo, SessionRepository)
