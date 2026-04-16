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
    get_agent_run_exception_mock,
    get_agent_invalid_structured_response_mock,
    ContextMock,
)


def test_get_agent(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(chatbot_module, "get_chatbot_settings", get_chatbot_settings_mock)
    monkeypatch.setattr(chatbot_module, "get_llm", get_llm_mock)
    monkeypatch.setattr(chatbot_module, "get_embed_model", get_embed_model_mock)
    monkeypatch.setattr(chatbot_module, "load_tools", load_tools_mock)
    monkeypatch.setattr(chatbot_module, "get_agent_yaml_settings", get_agent_yaml_settings_mock)
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
    monkeypatch.setattr(chatbot_module, "get_chatbot_settings", get_chatbot_settings_mock)
    monkeypatch.setattr(chatbot_module, "get_llm", get_llm_mock)
    monkeypatch.setattr(chatbot_module, "get_embed_model", get_embed_model_mock)
    monkeypatch.setattr(chatbot_module, "load_tools", load_tools_mock)
    monkeypatch.setattr(chatbot_module, "get_agent_yaml_settings", get_agent_yaml_settings_mock)
    monkeypatch.setattr(chatbot_module, "get_agent", get_agent_run_exception_mock)
    monkeypatch.setattr(chatbot_module, "Context", ContextMock)

    get_chatbot.cache_clear()
    chatbot: Chatbot = get_chatbot()
    response: Dict[str, Any] = await chatbot.chat_generate(
        query_str="What knowledge base have you got?",
        messages=chat_history,
    )

    assert response["response"] == "Sorry, I could not process your request.\nPlease try rephrasing your question."
    assert response["tags"] == []
    assert response["context"] == []

@pytest.mark.asyncio
async def test_chat_generate_invalid_structured_response(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(chatbot_module, "get_chatbot_settings", get_chatbot_settings_mock)
    monkeypatch.setattr(chatbot_module, "get_llm", get_llm_mock)
    monkeypatch.setattr(chatbot_module, "get_embed_model", get_embed_model_mock)
    monkeypatch.setattr(chatbot_module, "load_tools", load_tools_mock)
    monkeypatch.setattr(chatbot_module, "get_agent_yaml_settings", get_agent_yaml_settings_mock)
    monkeypatch.setattr(chatbot_module, "get_agent", get_agent_invalid_structured_response_mock)
    monkeypatch.setattr(chatbot_module, "Context", ContextMock)

    get_chatbot.cache_clear()
    chatbot: Chatbot = get_chatbot()
    response: Dict[str, Any] = await chatbot.chat_generate(
        query_str="What knowledge base have you got?",
        messages=chat_history,
    )

    assert response["response"] == "Sorry, I could not process your request.\nPlease try rephrasing your question."
    assert response["tags"] == []
    assert response["context"] == []

@pytest.mark.asyncio
async def test_chat_generate(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(chatbot_module, "get_chatbot_settings", get_chatbot_settings_mock)
    monkeypatch.setattr(chatbot_module, "get_llm", get_llm_mock)
    monkeypatch.setattr(chatbot_module, "get_embed_model", get_embed_model_mock)
    monkeypatch.setattr(chatbot_module, "load_tools", load_tools_mock)
    monkeypatch.setattr(chatbot_module, "get_agent_yaml_settings", get_agent_yaml_settings_mock)
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
    assert response["context"] == {
        "file1.pdf": [{"chunk_id": "1", "content": "some content", "score": 0.9}]
    }
