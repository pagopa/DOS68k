import pytest
from unittest.mock import MagicMock

import dos_utility.agent as agent_mod
import dos_utility.agent.llamaindex_google as google_mod
import dos_utility.agent.llamaindex_openai as openai_mod

from dos_utility.agent import (
    AgentConfig,
    AgentInitializationException,
    AgentInterface,
    ChatGenerationException,
    get_agent_client,
)
from test.agent.mocks import (
    get_agent_settings_google_mock,
    get_agent_settings_openai_mock,
    get_agent_settings_unknown_mock,
)


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


def test_agent_initialization_exception_message():
    exc = AgentInitializationException(msg="bad config")
    assert "bad config" in str(exc)
    assert "Agent initialization failed" in str(exc)


def test_chat_generation_exception_message():
    exc = ChatGenerationException(msg="provider error")
    assert "provider error" in str(exc)
    assert "Chat generation failed" in str(exc)


# ---------------------------------------------------------------------------
# AgentInterface — abstract contract
# ---------------------------------------------------------------------------


def test_agent_interface_not_instantiable():
    with pytest.raises(TypeError):
        AgentInterface()


# ---------------------------------------------------------------------------
# get_agent_client — provider routing
# ---------------------------------------------------------------------------


def test_get_agent_client_routes_to_openai(monkeypatch: pytest.MonkeyPatch):
    fake_agent = MagicMock(spec=AgentInterface)
    monkeypatch.setattr(agent_mod, "get_agent_settings", get_agent_settings_openai_mock)
    monkeypatch.setattr(
        openai_mod, "get_llamaindex_openai_agent", lambda **kw: fake_agent
    )

    result = get_agent_client(rag_tools=[], agent_config=AgentConfig())

    assert result is fake_agent


def test_get_agent_client_routes_to_google(monkeypatch: pytest.MonkeyPatch):
    fake_agent = MagicMock(spec=AgentInterface)
    monkeypatch.setattr(agent_mod, "get_agent_settings", get_agent_settings_google_mock)
    monkeypatch.setattr(
        google_mod, "get_llamaindex_google_agent", lambda **kw: fake_agent
    )

    result = get_agent_client(rag_tools=[], agent_config=AgentConfig())

    assert result is fake_agent


def test_get_agent_client_passes_kwargs_to_provider(monkeypatch: pytest.MonkeyPatch):
    captured = {}

    def fake_openai_factory(**kw):
        captured.update(kw)
        return MagicMock(spec=AgentInterface)

    from dos_utility.agent.models import RagToolSpec
    from pydantic import BaseModel

    class MySchema(BaseModel):
        answer: str

    rag_tools = [RagToolSpec(index_id="idx", name="tool", description="desc")]
    config = AgentConfig(name="bot")

    monkeypatch.setattr(agent_mod, "get_agent_settings", get_agent_settings_openai_mock)
    monkeypatch.setattr(openai_mod, "get_llamaindex_openai_agent", fake_openai_factory)

    get_agent_client(rag_tools=rag_tools, agent_config=config, output_schema=MySchema)

    assert captured["rag_tools"] == rag_tools
    assert captured["agent_config"] == config
    assert captured["output_schema"] is MySchema


def test_get_agent_client_raises_for_unsupported_provider(
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setattr(
        agent_mod, "get_agent_settings", get_agent_settings_unknown_mock
    )

    with pytest.raises(AgentInitializationException):
        get_agent_client(rag_tools=[], agent_config=AgentConfig())
