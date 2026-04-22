import pytest

from llama_index.core.agent.workflow import ReActAgent
from llama_index.core.llms.llm import LLM

from src.modules.chatbot import agent as agent_module
from src.modules.chatbot.agent import get_agent

from test.modules.chatbot.mocks import GoogleGenAIMock
from test.modules.chatbot.agent.mocks import ReActAgentMock


def test_get_agent(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(agent_module, "ReActAgent", ReActAgentMock)

    llm: LLM = GoogleGenAIMock()
    agent: ReActAgent = get_agent(llm=llm)

    assert isinstance(agent, ReActAgent)


def test_get_agent_with_optional_parameters(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(agent_module, "ReActAgent", ReActAgentMock)

    llm: LLM = GoogleGenAIMock()
    agent: ReActAgent = get_agent(
        llm=llm,
        name="TestAgent",
        description="Test description",
        system_header="Test system header",
    )

    assert isinstance(agent, ReActAgent)
