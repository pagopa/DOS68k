import pytest

from fastapi import HTTPException

from src.modules.sessions.service import SessionService, get_session_service
from src.modules.sessions.env import get_session_settings

from test.modules.sessions.mocks import (
    MockSessionRepository,
    MockSessionRepositoryNotFound,
    MockQueryRepository,
    MockQueryRepositoryEmpty,
    MOCK_SESSION_ID,
    MOCK_USER_ID,
)


@pytest.fixture(autouse=True)
def setup_env(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("SESSION_EXPIRATION_DAYS", "30")
    get_session_settings.cache_clear()


# ---------------------------------------------------------------------------
# get_session
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_session_success():
    service = SessionService(
        session_repository=MockSessionRepository(),
        query_repository=MockQueryRepository(),
    )
    result = await service.get_session(session_id=MOCK_SESSION_ID, user_id=MOCK_USER_ID)

    assert result["id"] == MOCK_SESSION_ID
    assert result["user_id"] == MOCK_USER_ID
    assert result["title"] == "Test Session"
    assert "created_at" in result
    assert "expires_at" in result


@pytest.mark.asyncio
async def test_get_session_not_found():
    service = SessionService(
        session_repository=MockSessionRepositoryNotFound(),
        query_repository=MockQueryRepository(),
    )

    with pytest.raises(HTTPException) as exc_info:
        await service.get_session(session_id=MOCK_SESSION_ID, user_id=MOCK_USER_ID)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Session not found"


# ---------------------------------------------------------------------------
# get_sessions
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_sessions_returns_list():
    service = SessionService(
        session_repository=MockSessionRepository(),
        query_repository=MockQueryRepository(),
    )
    result = await service.get_sessions(user_id=MOCK_USER_ID)

    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0]["id"] == MOCK_SESSION_ID
    assert result[0]["user_id"] == MOCK_USER_ID


@pytest.mark.asyncio
async def test_get_sessions_returns_empty():
    service = SessionService(
        session_repository=MockSessionRepositoryNotFound(),
        query_repository=MockQueryRepositoryEmpty(),
    )
    result = await service.get_sessions(user_id=MOCK_USER_ID)

    assert result == []


# ---------------------------------------------------------------------------
# create_session
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_session_permanent():
    service = SessionService(
        session_repository=MockSessionRepository(),
        query_repository=MockQueryRepository(),
    )
    result = await service.create_session(
        user_id=MOCK_USER_ID,
        session_data={"title": "My Session"},
        is_temporary=False,
    )

    assert result["id"] == MOCK_SESSION_ID
    assert result["user_id"] == MOCK_USER_ID
    assert result["title"] == "My Session"
    assert result["expires_at"] is None  # permanent sessions have no expiration


@pytest.mark.asyncio
async def test_create_session_temporary():
    service = SessionService(
        session_repository=MockSessionRepository(),
        query_repository=MockQueryRepository(),
    )
    result = await service.create_session(
        user_id=MOCK_USER_ID,
        session_data={"title": "Temporary Session"},
        is_temporary=True,
    )

    assert result["id"] == MOCK_SESSION_ID
    # Temporary session: MockSessionRepository returns expiresAt=None from MOCK_SESSION_ITEM,
    # so the formatted result stays None (real repo would compute expiration).
    assert "expires_at" in result


# ---------------------------------------------------------------------------
# delete_session
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_delete_session_success():
    service = SessionService(
        session_repository=MockSessionRepository(),
        query_repository=MockQueryRepository(),
    )

    # Should complete without raising any exception
    await service.delete_session(session_id=MOCK_SESSION_ID, user_id=MOCK_USER_ID)


@pytest.mark.asyncio
async def test_delete_session_also_deletes_queries():
    """Deleting a session cascades to delete all associated queries."""
    deleted_queries: list = []

    class TrackingQueryRepository(MockQueryRepository):
        async def delete_query(self, query_id: str, session_id: str) -> None:
            deleted_queries.append(query_id)

    service = SessionService(
        session_repository=MockSessionRepository(),
        query_repository=TrackingQueryRepository(),
    )
    await service.delete_session(session_id=MOCK_SESSION_ID, user_id=MOCK_USER_ID)

    # MockQueryRepository.get_queries returns 1 item, so 1 delete should happen
    assert len(deleted_queries) == 1


@pytest.mark.asyncio
async def test_delete_session_not_found():
    service = SessionService(
        session_repository=MockSessionRepositoryNotFound(),
        query_repository=MockQueryRepository(),
    )

    with pytest.raises(HTTPException) as exc_info:
        await service.delete_session(session_id=MOCK_SESSION_ID, user_id=MOCK_USER_ID)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Session not found"


# ---------------------------------------------------------------------------
# clear_session
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_clear_session_success():
    service = SessionService(
        session_repository=MockSessionRepository(),
        query_repository=MockQueryRepository(),
    )
    result = await service.clear_session(
        session_id=MOCK_SESSION_ID, user_id=MOCK_USER_ID
    )

    assert result["id"] == MOCK_SESSION_ID
    assert result["userId"] == MOCK_USER_ID


@pytest.mark.asyncio
async def test_clear_session_not_found():
    service = SessionService(
        session_repository=MockSessionRepositoryNotFound(),
        query_repository=MockQueryRepository(),
    )

    with pytest.raises(HTTPException) as exc_info:
        await service.clear_session(session_id=MOCK_SESSION_ID, user_id=MOCK_USER_ID)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Session not found"


# ---------------------------------------------------------------------------
# get_session_service
# ---------------------------------------------------------------------------


def test_get_session_service_returns_instance():
    service = get_session_service(
        session_repository=MockSessionRepository(),
        query_repository=MockQueryRepository(),
    )

    assert isinstance(service, SessionService)
