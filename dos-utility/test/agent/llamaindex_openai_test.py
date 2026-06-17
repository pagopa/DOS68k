import pytest
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import dos_utility.agent.llamaindex_openai.implementation as impl_mod

from dos_utility.agent.llamaindex_openai.implementation import LlamaIndexOpenAIAgent
from dos_utility.agent.models import AgentResponse, ChatTurn
from dos_utility.agent.exceptions import ChatGenerationException


def _make_agent() -> LlamaIndexOpenAIAgent:
    agent = object.__new__(LlamaIndexOpenAIAgent)
    agent._llm = AsyncMock()
    agent._agent = AsyncMock()
    agent._embed_model = MagicMock()
    agent._tool_names = []
    return agent


def _make_node(filename: str, chunk_id: int, content: str, score):
    return SimpleNamespace(
        metadata={"filename": filename, "chunk_id": chunk_id},
        text=content,
        score=score,
    )


def _make_tool_call(source_nodes):
    raw_output = SimpleNamespace(source_nodes=source_nodes)
    tool_output = SimpleNamespace(raw_output=raw_output)
    return SimpleNamespace(tool_output=tool_output)


# ---------------------------------------------------------------------------
# _history_to_chat_messages
# ---------------------------------------------------------------------------


def test_history_none_returns_empty():
    agent = _make_agent()
    assert agent._history_to_chat_messages(history=None) == []


def test_history_empty_list_returns_empty():
    agent = _make_agent()
    assert agent._history_to_chat_messages(history=[]) == []


def test_history_answered_turn_produces_two_messages():
    agent = _make_agent()
    result = agent._history_to_chat_messages([ChatTurn(question="Q", answer="A")])
    assert len(result) == 2
    assert result[0].content == "Q"
    assert result[1].content == "A"


def test_history_unanswered_turn_produces_one_message():
    agent = _make_agent()
    result = agent._history_to_chat_messages([ChatTurn(question="Q", answer=None)])
    assert len(result) == 1
    assert result[0].content == "Q"


def test_history_answer_is_stripped():
    agent = _make_agent()
    result = agent._history_to_chat_messages([ChatTurn(question="Q", answer="  hi  ")])
    assert result[1].content == "hi"


def test_history_multiple_turns_ordered():
    agent = _make_agent()
    result = agent._history_to_chat_messages(
        [
            ChatTurn(question="Q1", answer="A1"),
            ChatTurn(question="Q2", answer="A2"),
        ]
    )
    contents = [m.content for m in result]
    assert contents == ["Q1", "A1", "Q2", "A2"]


# ---------------------------------------------------------------------------
# _context_from_tool_calls
# ---------------------------------------------------------------------------


def test_context_empty_tool_calls():
    agent = _make_agent()
    assert agent._context_from_tool_calls(tool_calls=[]) == []


def test_context_raw_output_without_source_nodes_attr():
    agent = _make_agent()
    raw_output = SimpleNamespace()  # no source_nodes attribute
    call = SimpleNamespace(tool_output=SimpleNamespace(raw_output=raw_output))
    result = agent._context_from_tool_calls(tool_calls=[call])
    assert result == []


def test_context_from_tool_calls_maps_node_fields():
    agent = _make_agent()
    node = _make_node("doc.txt", 3, "body text", 0.85)
    result = agent._context_from_tool_calls(tool_calls=[_make_tool_call([node])])
    assert len(result) == 1
    assert result[0].filename == "doc.txt"
    assert result[0].chunk_id == 3
    assert result[0].content == "body text"
    assert result[0].score == 0.85


def test_context_sorted_by_score_descending():
    agent = _make_agent()
    nodes = [
        _make_node("a.txt", 0, "low", 0.3),
        _make_node("b.txt", 1, "high", 0.9),
        _make_node("c.txt", 2, "mid", 0.6),
    ]
    result = agent._context_from_tool_calls(tool_calls=[_make_tool_call(nodes)])
    scores = [c.score for c in result]
    assert scores == sorted(scores, reverse=True)


def test_context_none_score_goes_last():
    agent = _make_agent()
    nodes = [
        _make_node("a.txt", 0, "no-score", None),
        _make_node("b.txt", 1, "scored", 0.5),
    ]
    result = agent._context_from_tool_calls(tool_calls=[_make_tool_call(nodes)])
    assert result[0].score == 0.5
    assert result[1].score is None


def test_context_chunk_id_falls_back_to_zero_when_missing():
    agent = _make_agent()
    node = SimpleNamespace(
        metadata={"filename": "f.txt"},  # no chunk_id key
        text="t",
        score=None,
    )
    result = agent._context_from_tool_calls(tool_calls=[_make_tool_call([node])])
    assert result[0].chunk_id == 0


# ---------------------------------------------------------------------------
# chat_generate
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_chat_generate_happy_path(monkeypatch: pytest.MonkeyPatch):
    agent = _make_agent()
    fake_ctx = MagicMock()
    monkeypatch.setattr(
        impl_mod, "Context", MagicMock(from_dict=MagicMock(return_value=fake_ctx))
    )
    engine_response = SimpleNamespace(
        structured_response={"response": "The answer"},
        tool_calls=[],
    )
    agent._agent.run = AsyncMock(return_value=engine_response)

    result = await agent.chat_generate(query="What is DOS68K?")

    assert isinstance(result, AgentResponse)
    assert result.response == "The answer"
    assert result.context == []


@pytest.mark.asyncio
async def test_chat_generate_passes_history(monkeypatch: pytest.MonkeyPatch):
    agent = _make_agent()
    monkeypatch.setattr(
        impl_mod, "Context", MagicMock(from_dict=MagicMock(return_value=MagicMock()))
    )
    engine_response = SimpleNamespace(
        structured_response={"response": "ok"},
        tool_calls=[],
    )
    agent._agent.run = AsyncMock(return_value=engine_response)

    history = [ChatTurn(question="prev", answer="prev-answer")]
    await agent.chat_generate(query="q", history=history)

    _, kwargs = agent._agent.run.call_args
    assert len(kwargs["chat_history"]) == 2


@pytest.mark.asyncio
async def test_chat_generate_agent_raises_chat_generation_exception(
    monkeypatch: pytest.MonkeyPatch,
):
    agent = _make_agent()
    monkeypatch.setattr(
        impl_mod, "Context", MagicMock(from_dict=MagicMock(return_value=MagicMock()))
    )
    agent._agent.run = AsyncMock(side_effect=RuntimeError("llm down"))

    with pytest.raises(ChatGenerationException):
        await agent.chat_generate(query="q")


@pytest.mark.asyncio
async def test_chat_generate_raises_when_structured_response_is_none(
    monkeypatch: pytest.MonkeyPatch,
):
    agent = _make_agent()
    monkeypatch.setattr(
        impl_mod, "Context", MagicMock(from_dict=MagicMock(return_value=MagicMock()))
    )
    agent._agent.run = AsyncMock(
        return_value=SimpleNamespace(structured_response=None, tool_calls=[])
    )

    with pytest.raises(ChatGenerationException):
        await agent.chat_generate(query="q")


@pytest.mark.asyncio
async def test_chat_generate_raises_when_response_key_missing(
    monkeypatch: pytest.MonkeyPatch,
):
    agent = _make_agent()
    monkeypatch.setattr(
        impl_mod, "Context", MagicMock(from_dict=MagicMock(return_value=MagicMock()))
    )
    agent._agent.run = AsyncMock(
        return_value=SimpleNamespace(
            structured_response={"other_key": "value"}, tool_calls=[]
        )
    )

    with pytest.raises(ChatGenerationException):
        await agent.chat_generate(query="q")


# ---------------------------------------------------------------------------
# is_healthy
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_is_healthy_returns_true_when_llm_succeeds():
    agent = _make_agent()
    agent._llm.acomplete = AsyncMock(return_value="pong")
    assert await agent.is_healthy() is True


@pytest.mark.asyncio
async def test_is_healthy_returns_false_when_llm_raises():
    agent = _make_agent()
    agent._llm.acomplete = AsyncMock(side_effect=RuntimeError("unreachable"))
    assert await agent.is_healthy() is False


# ---------------------------------------------------------------------------
# close
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_close_returns_none():
    agent = _make_agent()
    assert await agent.close() is None
