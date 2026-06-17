import json
import pytest

from uuid import UUID
from fastapi import HTTPException

from src.modules.evaluate.service import EvaluationService, get_evaluation_service

from test.modules.evaluate.mocks import (
    MockNoSQLClient,
    MockQueueClient,
    MOCK_SESSION_ID,
    MOCK_QUERY_ID,
    MOCK_USER_ID,
    MOCK_QUERY_ITEM,
)


# ---------------------------------------------------------------------------
# create_simple_feedback
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_simple_feedback_success():
    nosql = MockNoSQLClient(update_returns={"id": MOCK_QUERY_ID})
    service = EvaluationService(nosql=nosql, queue=MockQueueClient())

    result = await service.create_simple_feedback(
        user_id=MOCK_USER_ID,
        session_id=UUID(MOCK_SESSION_ID),
        query_id=UUID(MOCK_QUERY_ID),
        feedback=1,
    )

    assert result["feedback"] == 1
    assert nosql.update_calls[0]["fields"] == {"feedback": 1}
    assert nosql.update_calls[0]["key"] == {
        "sessionId": MOCK_SESSION_ID,
        "id": MOCK_QUERY_ID,
    }


@pytest.mark.asyncio
async def test_create_simple_feedback_session_not_owned():
    nosql = MockNoSQLClient(sessions=[])
    service = EvaluationService(nosql=nosql, queue=MockQueueClient())

    with pytest.raises(HTTPException) as exc_info:
        await service.create_simple_feedback(
            user_id=MOCK_USER_ID,
            session_id=UUID(MOCK_SESSION_ID),
            query_id=UUID(MOCK_QUERY_ID),
            feedback=1,
        )

    assert exc_info.value.status_code == 404
    assert "Session" in exc_info.value.detail


@pytest.mark.asyncio
async def test_create_simple_feedback_query_not_found():
    # update_returns=None → update_item returns None → 404
    nosql = MockNoSQLClient(update_returns=None)
    service = EvaluationService(nosql=nosql, queue=MockQueueClient())

    with pytest.raises(HTTPException) as exc_info:
        await service.create_simple_feedback(
            user_id=MOCK_USER_ID,
            session_id=UUID(MOCK_SESSION_ID),
            query_id=UUID(MOCK_QUERY_ID),
            feedback=-1,
        )

    assert exc_info.value.status_code == 404
    assert "Query" in exc_info.value.detail


# ---------------------------------------------------------------------------
# evaluate
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_evaluate_enqueues_message_and_returns_queued():
    queue = MockQueueClient()
    service = EvaluationService(nosql=MockNoSQLClient(), queue=queue)

    result = await service.evaluate(
        query_id=UUID(MOCK_QUERY_ID),
        session_id=UUID(MOCK_SESSION_ID),
    )

    assert result == {
        "query_id": MOCK_QUERY_ID,
        "session_id": MOCK_SESSION_ID,
        "status": "queued",
    }
    assert len(queue.enqueued) == 1
    payload = json.loads(queue.enqueued[0].decode("utf-8"))
    assert payload == {"messageId": MOCK_QUERY_ID, "sessionId": MOCK_SESSION_ID}


@pytest.mark.asyncio
async def test_evaluate_query_not_found():
    service = EvaluationService(
        nosql=MockNoSQLClient(queries=[]),
        queue=MockQueueClient(),
    )

    with pytest.raises(HTTPException) as exc_info:
        await service.evaluate(
            query_id=UUID(MOCK_QUERY_ID),
            session_id=UUID(MOCK_SESSION_ID),
        )

    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_evaluate_already_evaluated_returns_409():
    evaluated_query = {**MOCK_QUERY_ITEM, "isEvaluated": True}
    queue = MockQueueClient()
    service = EvaluationService(
        nosql=MockNoSQLClient(queries=[evaluated_query]),
        queue=queue,
    )

    with pytest.raises(HTTPException) as exc_info:
        await service.evaluate(
            query_id=UUID(MOCK_QUERY_ID),
            session_id=UUID(MOCK_SESSION_ID),
        )

    assert exc_info.value.status_code == 409
    assert len(queue.enqueued) == 0


# ---------------------------------------------------------------------------
# evaluate_all
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_evaluate_all_enqueues_queries_with_feedback():
    queries = [
        {**MOCK_QUERY_ITEM, "id": "q-1", "feedback": 1, "isEvaluated": False},
        {**MOCK_QUERY_ITEM, "id": "q-2", "feedback": -1, "isEvaluated": False},
        {**MOCK_QUERY_ITEM, "id": "q-3", "feedback": 0, "isEvaluated": False},
    ]
    queue = MockQueueClient()
    service = EvaluationService(
        nosql=MockNoSQLClient(queries=queries),
        queue=queue,
    )

    result = await service.evaluate_all(session_id=UUID(MOCK_SESSION_ID))

    enqueued_ids = {json.loads(m.decode("utf-8"))["messageId"] for m in queue.enqueued}
    # With only 3 queries total and EVALUATE_UPPER_LIMIT=50, all three are selected
    # (q-1, q-2 by feedback; q-3 fills remaining slots).
    assert enqueued_ids == {"q-1", "q-2", "q-3"}
    assert len(result["evaluations"]) == 3


@pytest.mark.asyncio
async def test_evaluate_all_skips_already_evaluated():
    queries = [
        {**MOCK_QUERY_ITEM, "id": "q-1", "feedback": 1, "isEvaluated": True},
        {**MOCK_QUERY_ITEM, "id": "q-2", "feedback": 1, "isEvaluated": False},
    ]
    queue = MockQueueClient()
    service = EvaluationService(
        nosql=MockNoSQLClient(queries=queries),
        queue=queue,
    )

    result = await service.evaluate_all(session_id=UUID(MOCK_SESSION_ID))

    enqueued_ids = [json.loads(m.decode("utf-8"))["messageId"] for m in queue.enqueued]
    assert enqueued_ids == ["q-2"]
    assert [e["query_id"] for e in result["evaluations"]] == ["q-2"]


@pytest.mark.asyncio
async def test_evaluate_all_empty_when_no_queries():
    queue = MockQueueClient()
    service = EvaluationService(
        nosql=MockNoSQLClient(queries=[]),
        queue=queue,
    )

    result = await service.evaluate_all(session_id=UUID(MOCK_SESSION_ID))

    assert result == {"evaluations": []}
    assert queue.enqueued == []


# ---------------------------------------------------------------------------
# get_evaluation_service
# ---------------------------------------------------------------------------


def test_get_evaluation_service_returns_instance():
    service = get_evaluation_service(nosql=MockNoSQLClient(), queue=MockQueueClient())

    assert isinstance(service, EvaluationService)
