from typing import List, Optional, Type
from pydantic import BaseModel

from .interface import AgentInterface
from .models import (
    AgentConfig,
    AgentResponse,
    ChatTurn,
    ContextChunk,
    RagToolSpec,
)
from .env import AgentProvider, AgentSettings, get_agent_settings
from .exceptions import AgentInitializationException, ChatGenerationException


__all__ = [
    "AgentInterface",
    "AgentConfig",
    "AgentResponse",
    "ChatTurn",
    "ContextChunk",
    "RagToolSpec",
    "AgentProvider",
    "AgentInitializationException",
    "ChatGenerationException",
    "get_agent_client",
]


def get_agent_client(
    *,
    rag_tools: List[RagToolSpec],
    agent_config: AgentConfig,
    output_schema: Optional[Type[BaseModel]] = None,
) -> AgentInterface:
    """Return the configured agent provider implementation.

    Selection is driven by the ``AGENT_PROVIDER`` environment variable.

    Args:
        rag_tools (List[RagToolSpec]): RAG tool specifications backed by a vector index.
        agent_config (AgentConfig): High-level agent metadata and system prompts.
        output_schema (Optional[Type[BaseModel]]): Optional Pydantic schema describing
            the structured response the agent must return. The shape of the schema
            is provider-agnostic: implementations are expected to coerce the
            model output into this contract.

    Returns:
        AgentInterface: A ready-to-use agent client.

    Raises:
        AgentInitializationException: If the selected provider cannot be initialized.

    Examples:
        >>> agent: AgentInterface = get_agent_client(
        >>>     rag_tools=[RagToolSpec(index_id="docs", name="docs_search", description="...")],
        >>>     agent_config=AgentConfig(system_prompt="You are ..."),
        >>>     output_schema=MyResponseSchema,
        >>> )
        >>> response = await agent.chat_generate(query="Hello")
    """
    settings: AgentSettings = get_agent_settings()

    if settings.AGENT_PROVIDER == AgentProvider.LLAMAINDEX_GOOGLE:
        from .llamaindex_google import get_llamaindex_google_agent

        return get_llamaindex_google_agent(
            rag_tools=rag_tools,
            agent_config=agent_config,
            output_schema=output_schema,
        )

    if settings.AGENT_PROVIDER == AgentProvider.LLAMAINDEX_OPENAI:
        from .llamaindex_openai import get_llamaindex_openai_agent

        return get_llamaindex_openai_agent(
            rag_tools=rag_tools,
            agent_config=agent_config,
            output_schema=output_schema,
        )

    raise AgentInitializationException(
        msg=f"Unsupported AGENT_PROVIDER: {settings.AGENT_PROVIDER!r}"
    )
