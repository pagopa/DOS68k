from typing import Callable, Type, Optional, Dict, Any, List
from llama_index.core.tools import BaseTool
from llama_index.core.llms.llm import LLM
from llama_index.core.agent.workflow import ReActAgent

from .settings import AgentYamlSettings, get_agent_yaml_settings

__all__ = [
    "get_agent",
    "AgentYamlSettings",
    "get_agent_yaml_settings",
]


def get_agent(
        llm: LLM,
        system_header: Optional[str] = None,
        system_prompt: Optional[str] = None,
        output_cls: Optional[Type] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        tools: List[BaseTool | Callable] | None = None,
    ) -> ReActAgent:
    """Create and configure a ReActAgent instance.

    Args:
        llm: LLM used for agent reasoning.
        system_header: Optional override for the ReAct formatter's system header template.
        system_prompt: Optional system prompt injected at the start of every conversation.
        output_cls: Optional Pydantic model class used for structured output parsing.
        name: Optional agent name.
        description: Optional description of the agent's role.
        tools: Optional list of tools the agent can call.

    Returns:
        ReActAgent: The configured agent.
    """
    react_agent_kwargs: Dict[str, Any] = {
        "llm": llm,
        "tools": tools,
        "system_prompt": system_prompt,
        "output_cls": output_cls,
    }

    if name is not None:
        react_agent_kwargs["name"] = name

    if description is not None:
        react_agent_kwargs["description"] = description

    agent: ReActAgent = ReActAgent(**react_agent_kwargs)

    if system_header is not None:
        agent.formatter.system_header = system_header

    return agent
