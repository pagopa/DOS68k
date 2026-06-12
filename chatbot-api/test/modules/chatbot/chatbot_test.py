import pytest

from typing import Any, Dict, List

from src.modules.chatbot import chatbot as chatbot_module
from src.modules.chatbot.chatbot import Chatbot, FALLBACK_RESPONSE, get_chatbot

from test.modules.chatbot.mocks import (
    FailingAgent,
    SuccessAgent,
    UnexpectedFailingAgent,
    build_get_agent_client_mock,
    get_agent_yaml_settings_mock,
    load_rag_tool_specs_mock,
)


chat_history: List[Dict[str, str]] = [
    {"question": "Who are you?", "answer": "I'm DOS68K"},
    {
        "question": "What can you do?",
        "answer": "I answer your questions based on the knowledge base you provided",
    },
]


def _patch_common(monkeypatch: pytest.MonkeyPatch, agent) -> None:
    monkeypatch.setattr(
        chatbot_module, "get_agent_yaml_settings", get_agent_yaml_settings_mock
    )
    monkeypatch.setattr(
        chatbot_module, "load_rag_tool_specs", load_rag_tool_specs_mock
    )
    monkeypatch.setattr(
        chatbot_module, "get_agent_client", build_get_agent_client_mock(agent)
    )
    get_chatbot.cache_clear()


def test_get_chatbot(monkeypatch: pytest.MonkeyPatch) -> None:
    _patch_common(monkeypatch, SuccessAgent())

    chatbot: Chatbot = get_chatbot()

    assert isinstance(chatbot, Chatbot)
    assert chatbot.tool_names == ["tool1"]


@pytest.mark.asyncio
async def test_chat_generate(monkeypatch: pytest.MonkeyPatch) -> None:
    _patch_common(monkeypatch, SuccessAgent())

    chatbot: Chatbot = get_chatbot()
    response: Dict[str, Any] = await chatbot.chat_generate(
        query_str="What knowledge base have you got?",
        messages=chat_history,
    )

    assert response["response"] == "Test answer"
    assert response["tags"] == []
    assert response["context"] == [
        {
            "filename": "file1.pdf",
            "chunk_id": "1",
            "content": "some content",
            "score": 0.9,
        }
    ]


@pytest.mark.asyncio
async def test_chat_generate_chat_generation_exception(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _patch_common(monkeypatch, FailingAgent())

    chatbot: Chatbot = get_chatbot()
    response: Dict[str, Any] = await chatbot.chat_generate(
        query_str="What knowledge base have you got?",
        messages=chat_history,
    )

    assert response["response"] == FALLBACK_RESPONSE
    assert response["tags"] == []
    assert response["context"] == []


@pytest.mark.asyncio
async def test_chat_generate_unexpected_exception(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _patch_common(monkeypatch, UnexpectedFailingAgent())

    chatbot: Chatbot = get_chatbot()
    response: Dict[str, Any] = await chatbot.chat_generate(
        query_str="What knowledge base have you got?",
        messages=chat_history,
    )

    assert response["response"] == FALLBACK_RESPONSE
    assert response["tags"] == []
    assert response["context"] == []


@pytest.mark.asyncio
async def test_chat_generate_no_history(monkeypatch: pytest.MonkeyPatch) -> None:
    _patch_common(monkeypatch, SuccessAgent())

    chatbot: Chatbot = get_chatbot()
    response: Dict[str, Any] = await chatbot.chat_generate(query_str="Hi")

    assert response["response"] == "Test answer"
