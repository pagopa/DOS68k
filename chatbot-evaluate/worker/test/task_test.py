"""Tests for the worker task pipeline.

These tests lock down behavior that other services in DOS68K depend on:
- chatbot-api reads `isEvaluated` to know which queries are still pending.
- DynamoDB rejects float values, so scores must be Decimal-wrapped.
- The contextualization step is what makes follow-up questions in a chat
  evaluable — regressions there silently degrade RAG-evaluation quality.
"""

import json
import pytest

from decimal import Decimal

from src.worker import task

from test.mocks import (
    MockEvaluator,
    MockLLM,
    MockNoSQLClient,
    MockTaskSettings,
    MOCK_QUERY_ID,
    MOCK_SESSION_ID,
    install_task_mocks,
    make_query_item,
)


def _body(session_id: str = MOCK_SESSION_ID, message_id: str = MOCK_QUERY_ID) -> bytes:
    return json.dumps({"sessionId": session_id, "messageId": message_id}).encode(
        "utf-8"
    )


# ---------------------------------------------------------------------------
# Question selection: contextualize iff there is a prior chat turn
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_single_message_session_skips_contextualization(
    monkeypatch: pytest.MonkeyPatch,
):
    """One message in the session → evaluate the original question verbatim.

    Regression risk: if the contextualization branch starts firing on
    single-turn sessions it would call the LLM with empty history and either
    hallucinate or fail — and we'd be evaluating the wrong question.
    """
    item = make_query_item(id=MOCK_QUERY_ID, question="What is Python?")
    nosql = MockNoSQLClient(items=[item])
    llm, _ = install_task_mocks(monkeypatch, nosql_client=nosql)

    await task.process_task(body=_body())

    assert llm.acomplete_calls == []
    assert MockEvaluator._last is not None
    assert MockEvaluator._last.evaluate_calls[0]["question"] == "What is Python?"


@pytest.mark.asyncio
async def test_multi_message_session_contextualizes_via_llm(
    monkeypatch: pytest.MonkeyPatch, tmp_path
):
    """With prior turns, the target question is rewritten by the LLM.

    The evaluator must receive the contextualized (stripped) text, not the
    raw user question — otherwise follow-ups like "and in Italy?" get scored
    without their conversational context.
    """
    config = tmp_path / "contextualize.yml"
    config.write_text("prompt: 'Q: {{ question }} HIST: {{ history }}'")

    prior = make_query_item(
        id="prior",
        question="What's the capital of France?",
        answer="Paris.",
        created_at="2024-01-01T00:00:00",
    )
    target = make_query_item(
        id=MOCK_QUERY_ID,
        question="And in Italy?",
        answer="Rome.",
        created_at="2024-01-02T00:00:00",
    )
    nosql = MockNoSQLClient(items=[prior, target])

    llm, _ = install_task_mocks(
        monkeypatch,
        nosql_client=nosql,
        llm=MockLLM(response_text="  What is the capital of Italy?  "),
        task_settings=MockTaskSettings(config_path=str(config)),
    )

    await task.process_task(body=_body())

    assert len(llm.acomplete_calls) == 1
    evaluate_call = MockEvaluator._last.evaluate_calls[0]
    assert evaluate_call["question"] == "What is the capital of Italy?"
    assert evaluate_call["answer"] == "Rome."


@pytest.mark.asyncio
async def test_target_message_at_head_of_session_skips_contextualization(
    monkeypatch: pytest.MonkeyPatch,
):
    """If the target message is the first chronologically, no history exists.

    Regression risk: history is built by walking the session in order and
    breaking when the target id is hit. A bug that walked past the break (or
    included the target itself in history) would corrupt contextualization.
    """
    target = make_query_item(
        id=MOCK_QUERY_ID,
        question="First question",
        created_at="2024-01-01T00:00:00",
    )
    later = make_query_item(
        id="later",
        question="Later question",
        created_at="2024-01-02T00:00:00",
    )
    nosql = MockNoSQLClient(items=[target, later])
    llm, _ = install_task_mocks(monkeypatch, nosql_client=nosql)

    await task.process_task(body=_body())

    assert llm.acomplete_calls == []
    assert MockEvaluator._last.evaluate_calls[0]["question"] == "First question"


@pytest.mark.asyncio
async def test_history_sorted_by_created_at_even_when_input_is_unordered(
    monkeypatch: pytest.MonkeyPatch, tmp_path
):
    """NoSQL queries do not guarantee insertion order — task must sort.

    Regression risk: a future NoSQL backend that returns items in scan order
    (not createdAt order) would silently produce a history with the wrong
    chronology, poisoning the contextualization prompt.
    """
    config = tmp_path / "contextualize.yml"
    config.write_text("prompt: '{{ question }} {{ history }}'")

    older = make_query_item(
        id="older", question="Q-older", created_at="2024-01-01T00:00:00"
    )
    middle = make_query_item(
        id="middle", question="Q-middle", created_at="2024-01-02T00:00:00"
    )
    target = make_query_item(
        id=MOCK_QUERY_ID, question="Q-target", created_at="2024-01-03T00:00:00"
    )

    nosql = MockNoSQLClient(items=[target, older, middle])
    llm, _ = install_task_mocks(
        monkeypatch,
        nosql_client=nosql,
        task_settings=MockTaskSettings(config_path=str(config)),
    )

    await task.process_task(body=_body())

    # Two prior turns → contextualization fires once
    assert len(llm.acomplete_calls) == 1


# ---------------------------------------------------------------------------
# Persistence contract
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_persists_scores_as_decimal_and_marks_evaluated(
    monkeypatch: pytest.MonkeyPatch,
):
    """The update must use the composite key (sessionId, id), wrap scores in
    Decimal, and set isEvaluated=True.

    Each is a load-bearing contract:
    - Wrong key → DynamoDB silently writes nothing.
    - Float scores → DynamoDB rejects the write entirely.
    - Missing isEvaluated → chatbot-api keeps re-enqueueing the same query.
    """
    item = make_query_item()
    nosql = MockNoSQLClient(items=[item])
    install_task_mocks(monkeypatch, nosql_client=nosql)

    await task.process_task(body=_body())

    assert len(nosql.update_calls) == 1
    update = nosql.update_calls[0]
    assert update["table_name"] == "queries"
    assert update["key"] == {"sessionId": MOCK_SESSION_ID, "id": MOCK_QUERY_ID}

    fields = update["fields_to_update"]
    assert fields["isEvaluated"] is True
    assert set(fields["scores"].keys()) == {
        "relevancy",
        "faithfulness",
        "utilization",
    }
    assert all(isinstance(v, Decimal) for v in fields["scores"].values())


@pytest.mark.asyncio
async def test_evaluator_receives_context_chunks_as_string_list(
    monkeypatch: pytest.MonkeyPatch,
):
    """Context items are stored as dicts but the evaluator wants plain strings.

    Regression risk: passing the raw dicts would crash Ragas with an opaque
    error inside the metric implementation.
    """
    item = make_query_item(
        context=[
            {"content": "chunk-a", "score": 0.9},
            {"content": "chunk-b", "score": 0.8},
        ]
    )
    install_task_mocks(monkeypatch, nosql_client=MockNoSQLClient(items=[item]))

    await task.process_task(body=_body())

    assert MockEvaluator._last.evaluate_calls[0]["context"] == [
        "chunk-a",
        "chunk-b",
    ]


# ---------------------------------------------------------------------------
# Failure modes
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_missing_contextualization_config_raises(
    monkeypatch: pytest.MonkeyPatch,
):
    """When contextualization is required but the YAML is missing, fail loud.

    Regression risk: a silently-skipped contextualization step would score
    follow-up questions out of context and the bad data would land in NoSQL
    indistinguishable from a real evaluation.
    """
    prior = make_query_item(id="prior", created_at="2024-01-01T00:00:00")
    target = make_query_item(id=MOCK_QUERY_ID, created_at="2024-01-02T00:00:00")
    nosql = MockNoSQLClient(items=[prior, target])

    install_task_mocks(
        monkeypatch,
        nosql_client=nosql,
        task_settings=MockTaskSettings(config_path="/definitely/not/here.yml"),
    )

    with pytest.raises(FileNotFoundError):
        await task.process_task(body=_body())

    # And we must NOT have written a bogus evaluation to the DB.
    assert nosql.update_calls == []


@pytest.mark.asyncio
async def test_malformed_body_raises_before_touching_db(
    monkeypatch: pytest.MonkeyPatch,
):
    """A body without sessionId/messageId should fail fast.

    Regression risk: a partial parse that proceeds with empty ids could
    overwrite real records or query the wrong session.
    """
    item = make_query_item()
    nosql = MockNoSQLClient(items=[item])
    install_task_mocks(monkeypatch, nosql_client=nosql)

    with pytest.raises(KeyError):
        await task.process_task(body=b'{"unrelated": "field"}')

    assert nosql.update_calls == []
