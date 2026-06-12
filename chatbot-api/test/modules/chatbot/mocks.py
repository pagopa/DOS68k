from pathlib import Path
from typing import List, Optional, Self, Type

from pydantic import BaseModel

from dos_utility.agent import (
    AgentConfig,
    AgentInterface,
    AgentResponse,
    ChatGenerationException,
    ChatTurn,
    ContextChunk,
    RagToolSpec,
)

from src.modules.chatbot.agent.settings import AgentYamlSettings


# --- Stub AgentInterface implementations -----------------------------------


class _BaseStubAgent(AgentInterface):
    """Common no-op lifecycle for stub agents used in tests."""

    def __init__(self: Self) -> None:
        pass

    async def is_healthy(self: Self) -> bool:
        return True

    async def chat_generate(
        self: Self, query: str, history: Optional[List[ChatTurn]] = None
    ) -> AgentResponse:
        raise NotImplementedError

    async def close(self: Self) -> None:
        pass


class SuccessAgent(_BaseStubAgent):
    async def chat_generate(
        self: Self, query: str, history: Optional[List[ChatTurn]] = None
    ) -> AgentResponse:
        return AgentResponse(
            response="Test answer",
            tags=[],
            context=[
                ContextChunk(
                    filename="file1.pdf",
                    chunk_id="1",
                    content="some content",
                    score=0.9,
                )
            ],
        )


class FailingAgent(_BaseStubAgent):
    async def chat_generate(
        self: Self, query: str, history: Optional[List[ChatTurn]] = None
    ) -> AgentResponse:
        raise ChatGenerationException("boom")


class UnexpectedFailingAgent(_BaseStubAgent):
    async def chat_generate(
        self: Self, query: str, history: Optional[List[ChatTurn]] = None
    ) -> AgentResponse:
        raise RuntimeError("unexpected")


# --- Factory replacements --------------------------------------------------


def build_get_agent_client_mock(agent: AgentInterface):
    """Return a `get_agent_client` replacement that yields `agent`."""

    def _get_agent_client_mock(
        *,
        rag_tools: List[RagToolSpec],
        agent_config: AgentConfig,
        output_schema: Optional[Type[BaseModel]] = None,
    ) -> AgentInterface:
        return agent

    return _get_agent_client_mock


def get_agent_yaml_settings_mock(file: Path) -> AgentYamlSettings:
    return AgentYamlSettings(
        name="TestAgent",
        description="Test agent description",
    )


def load_rag_tool_specs_mock(config_dir: Path) -> List[RagToolSpec]:
    return [
        RagToolSpec(
            index_id="idx-1",
            name="tool1",
            description="Test tool 1",
        ),
    ]
