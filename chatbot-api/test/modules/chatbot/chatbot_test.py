import pytest

from typing import List, Dict, Any
from src.modules.chatbot import chatbot as chatbot_module
from src.modules.chatbot.chatbot import get_chatbot, Chatbot

from test.modules.chatbot.mocks import (
    get_chatbot_settings_mock,
    get_llm_mock,
    get_embed_model_mock,
    load_tools_mock,
    get_agent_yaml_settings_mock,
    get_agent_mock,
    make_agent_mock,
    get_agent_run_exception_mock,
    get_agent_invalid_structured_response_mock,
    ContextMock,
)


def test_get_agent(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(
        chatbot_module, "get_chatbot_settings", get_chatbot_settings_mock
    )
    monkeypatch.setattr(chatbot_module, "get_llm", get_llm_mock)
    monkeypatch.setattr(chatbot_module, "get_embed_model", get_embed_model_mock)
    monkeypatch.setattr(chatbot_module, "load_tools", load_tools_mock)
    monkeypatch.setattr(
        chatbot_module, "get_agent_yaml_settings", get_agent_yaml_settings_mock
    )
    monkeypatch.setattr(chatbot_module, "get_agent", get_agent_mock)

    get_chatbot.cache_clear()
    chatbot: Chatbot = get_chatbot()

    assert isinstance(chatbot, Chatbot)


chat_history: List[Dict[str, str]] = [
    {
        "question": "Who are you?",
        "answer": "I'm DOS68K",
    },
    {
        "question": "What can you do?",
        "answer": "I answer your questions based on the knowledge base you provided",
    },
]


@pytest.mark.asyncio
async def test_chat_generate_agent_run_exception(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(
        chatbot_module, "get_chatbot_settings", get_chatbot_settings_mock
    )
    monkeypatch.setattr(chatbot_module, "get_llm", get_llm_mock)
    monkeypatch.setattr(chatbot_module, "get_embed_model", get_embed_model_mock)
    monkeypatch.setattr(chatbot_module, "load_tools", load_tools_mock)
    monkeypatch.setattr(
        chatbot_module, "get_agent_yaml_settings", get_agent_yaml_settings_mock
    )
    monkeypatch.setattr(chatbot_module, "get_agent", get_agent_run_exception_mock)
    monkeypatch.setattr(chatbot_module, "Context", ContextMock)

    get_chatbot.cache_clear()
    chatbot: Chatbot = get_chatbot()
    response: Dict[str, Any] = await chatbot.chat_generate(
        query_str="What knowledge base have you got?",
        messages=chat_history,
    )

    assert (
        response["response"]
        == "Sorry, I could not process your request.\nPlease try rephrasing your question."
    )
    assert response["tags"] == []
    assert response["context"] == []


@pytest.mark.asyncio
async def test_chat_generate_invalid_structured_response(
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setattr(
        chatbot_module, "get_chatbot_settings", get_chatbot_settings_mock
    )
    monkeypatch.setattr(chatbot_module, "get_llm", get_llm_mock)
    monkeypatch.setattr(chatbot_module, "get_embed_model", get_embed_model_mock)
    monkeypatch.setattr(chatbot_module, "load_tools", load_tools_mock)
    monkeypatch.setattr(
        chatbot_module, "get_agent_yaml_settings", get_agent_yaml_settings_mock
    )
    monkeypatch.setattr(
        chatbot_module, "get_agent", get_agent_invalid_structured_response_mock
    )
    monkeypatch.setattr(chatbot_module, "Context", ContextMock)

    get_chatbot.cache_clear()
    chatbot: Chatbot = get_chatbot()
    response: Dict[str, Any] = await chatbot.chat_generate(
        query_str="What knowledge base have you got?",
        messages=chat_history,
    )

    assert (
        response["response"]
        == "Sorry, I could not process your request.\nPlease try rephrasing your question."
    )
    assert response["tags"] == []
    assert response["context"] == []


@pytest.mark.asyncio
async def test_chat_generate(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(
        chatbot_module, "get_chatbot_settings", get_chatbot_settings_mock
    )
    monkeypatch.setattr(chatbot_module, "get_llm", get_llm_mock)
    monkeypatch.setattr(chatbot_module, "get_embed_model", get_embed_model_mock)
    monkeypatch.setattr(chatbot_module, "load_tools", load_tools_mock)
    monkeypatch.setattr(
        chatbot_module, "get_agent_yaml_settings", get_agent_yaml_settings_mock
    )
    monkeypatch.setattr(chatbot_module, "get_agent", get_agent_mock)
    monkeypatch.setattr(chatbot_module, "Context", ContextMock)

    get_chatbot.cache_clear()
    chatbot: Chatbot = get_chatbot()
    response: Dict[str, Any] = await chatbot.chat_generate(
        query_str="What knowledge base have you got?",
        messages=chat_history,
    )

    assert response["response"] == "Test answer"
    assert response["tags"] == []
    assert response["context"] == [
        {
            "chunk_id": "1",
            "content": "some content",
            "score": 0.9,
            "filename": "file1.pdf",
            "url": "https://example.com/file1",
            "title": "File 1",
        }
    ]


async def _references_for(
    monkeypatch: pytest.MonkeyPatch,
    structured_response: Dict[str, Any],
    nodes_metadata: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Run chat_generate with the given agent output and return its references."""
    monkeypatch.setattr(
        chatbot_module, "get_chatbot_settings", get_chatbot_settings_mock
    )
    monkeypatch.setattr(chatbot_module, "get_llm", get_llm_mock)
    monkeypatch.setattr(chatbot_module, "get_embed_model", get_embed_model_mock)
    monkeypatch.setattr(chatbot_module, "load_tools", load_tools_mock)
    monkeypatch.setattr(
        chatbot_module, "get_agent_yaml_settings", get_agent_yaml_settings_mock
    )
    monkeypatch.setattr(
        chatbot_module,
        "get_agent",
        make_agent_mock(
            structured_response=structured_response, nodes_metadata=nodes_metadata
        ),
    )
    monkeypatch.setattr(chatbot_module, "Context", ContextMock)

    get_chatbot.cache_clear()
    chatbot: Chatbot = get_chatbot()
    response: Dict[str, Any] = await chatbot.chat_generate(query_str="A question")

    return response["references"]


TWO_CHUNKS: List[Dict[str, Any]] = [
    {"chunk_id": "1", "url": "https://example.com/a", "title": "Doc A"},
    {"chunk_id": "2", "url": "https://example.com/b", "title": "Doc B"},
]


@pytest.mark.asyncio
async def test_chat_generate_keeps_only_references_grounded_in_context(
    monkeypatch: pytest.MonkeyPatch,
):
    """The agent may invent or mangle a URL: a reference that is not among the
    retrieved chunks must never be handed to the caller as a source."""
    references: List[Dict[str, Any]] = await _references_for(
        monkeypatch,
        structured_response={
            "response": "Test answer",
            "references": [
                {"title": "Doc A", "url": "https://example.com/a"},
                {"title": "Hallucinated", "url": "https://example.com/does-not-exist"},
            ],
        },
        nodes_metadata=TWO_CHUNKS,
    )

    assert references == [{"title": "Doc A", "url": "https://example.com/a"}]


@pytest.mark.asyncio
async def test_chat_generate_falls_back_to_context_when_agent_cites_nothing_usable(
    monkeypatch: pytest.MonkeyPatch,
):
    """With no citable reference left, the retrieved chunks are still real sources:
    the caller must get them rather than an empty list."""
    references: List[Dict[str, Any]] = await _references_for(
        monkeypatch,
        structured_response={
            "response": "Test answer",
            "references": [{"title": "Hallucinated", "url": "https://elsewhere.com/x"}],
        },
        nodes_metadata=TWO_CHUNKS,
    )

    assert references == [
        {"title": "Doc A", "url": "https://example.com/a"},
        {"title": "Doc B", "url": "https://example.com/b"},
    ]


@pytest.mark.asyncio
async def test_chat_generate_falls_back_to_context_when_agent_omits_references(
    monkeypatch: pytest.MonkeyPatch,
):
    references: List[Dict[str, Any]] = await _references_for(
        monkeypatch,
        structured_response={"response": "Test answer"},
        nodes_metadata=TWO_CHUNKS,
    )

    assert references == [
        {"title": "Doc A", "url": "https://example.com/a"},
        {"title": "Doc B", "url": "https://example.com/b"},
    ]


@pytest.mark.asyncio
async def test_chat_generate_deduplicates_references_by_url(
    monkeypatch: pytest.MonkeyPatch,
):
    """Several chunks come from the same document: it must be cited once."""
    references: List[Dict[str, Any]] = await _references_for(
        monkeypatch,
        structured_response={
            "response": "Test answer",
            "references": [
                {"title": "Doc A", "url": "https://example.com/a"},
                {"title": "Doc A", "url": "https://example.com/a"},
            ],
        },
        nodes_metadata=[
            {"chunk_id": "1", "url": "https://example.com/a", "title": "Doc A"},
            {"chunk_id": "2", "url": "https://example.com/a", "title": "Doc A"},
        ],
    )

    assert references == [{"title": "Doc A", "url": "https://example.com/a"}]


@pytest.mark.asyncio
async def test_chat_generate_returns_no_references_without_urls_in_context(
    monkeypatch: pytest.MonkeyPatch,
):
    """A chunk with no URL cannot be cited, so nothing is grounded."""
    references: List[Dict[str, Any]] = await _references_for(
        monkeypatch,
        structured_response={
            "response": "Test answer",
            "references": [{"title": "Doc A", "url": "https://example.com/a"}],
        },
        nodes_metadata=[{"chunk_id": "1", "filename": "file1.pdf"}],
    )

    assert references == []
