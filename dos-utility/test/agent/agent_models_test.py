import pytest

from dos_utility.agent.models import (
    AgentConfig,
    AgentResponse,
    ChatTurn,
    ContextChunk,
    RagToolSpec,
)


# ---------------------------------------------------------------------------
# ChatTurn
# ---------------------------------------------------------------------------


def test_chat_turn_answer_defaults_to_none():
    turn = ChatTurn(question="hi")
    assert turn.answer is None


def test_chat_turn_with_answer():
    turn = ChatTurn(question="hi", answer="hello")
    assert turn.answer == "hello"


def test_chat_turn_requires_question():
    with pytest.raises(Exception):
        ChatTurn()


# ---------------------------------------------------------------------------
# ContextChunk
# ---------------------------------------------------------------------------


def test_context_chunk_score_defaults_to_none():
    chunk = ContextChunk(filename="doc.txt", chunk_id=1, content="text")
    assert chunk.score is None


def test_context_chunk_with_score():
    chunk = ContextChunk(filename="doc.txt", chunk_id=1, content="text", score=0.9)
    assert chunk.score == 0.9


def test_context_chunk_fields():
    chunk = ContextChunk(
        filename="file.pdf", chunk_id=42, content="body text", score=0.7
    )
    assert chunk.filename == "file.pdf"
    assert chunk.chunk_id == 42
    assert chunk.content == "body text"


# ---------------------------------------------------------------------------
# AgentResponse
# ---------------------------------------------------------------------------


def test_agent_response_tags_and_context_default_to_empty():
    resp = AgentResponse(response="answer")
    assert resp.tags == []
    assert resp.context == []


def test_agent_response_with_tags_and_context():
    chunk = ContextChunk(filename="f", chunk_id=0, content="c")
    resp = AgentResponse(response="answer", tags=["ai", "rag"], context=[chunk])
    assert resp.tags == ["ai", "rag"]
    assert len(resp.context) == 1
    assert resp.context[0].filename == "f"


def test_agent_response_requires_response_field():
    with pytest.raises(Exception):
        AgentResponse()


# ---------------------------------------------------------------------------
# RagToolSpec
# ---------------------------------------------------------------------------


def test_rag_tool_spec_optional_fields_default_to_none():
    spec = RagToolSpec(index_id="idx", name="search_tool", description="Searches docs")
    assert spec.similarity_top_k is None
    assert spec.qa_prompt is None
    assert spec.refine_prompt is None


def test_rag_tool_spec_with_all_fields():
    spec = RagToolSpec(
        index_id="idx",
        name="search_tool",
        description="desc",
        similarity_top_k=10,
        qa_prompt="{context_str} {query_str}",
        refine_prompt="{existing_answer} {context_msg}",
    )
    assert spec.similarity_top_k == 10
    assert spec.qa_prompt is not None
    assert spec.refine_prompt is not None


# ---------------------------------------------------------------------------
# AgentConfig
# ---------------------------------------------------------------------------


def test_agent_config_all_fields_default_to_none():
    config = AgentConfig()
    assert config.name is None
    assert config.description is None
    assert config.system_prompt is None
    assert config.system_header is None


def test_agent_config_with_values():
    config = AgentConfig(
        name="my-agent",
        description="A helpful assistant",
        system_prompt="You are helpful.",
        system_header="Think step by step.",
    )
    assert config.name == "my-agent"
    assert config.system_prompt == "You are helpful."
