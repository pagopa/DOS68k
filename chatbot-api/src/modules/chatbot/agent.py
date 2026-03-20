import yaml

from pathlib import Path
from typing import Callable, Type, Optional, Dict, Any, List
from pydantic import BaseModel
from llama_index.core.tools import BaseTool
from llama_index.core.llms.llm import LLM
from llama_index.core.agent.workflow import ReActAgent


DEFAULT_AGENT_CONFIG: Path = Path(__file__).parent / "agent.yaml"


class AgentConfig(BaseModel):
    system_prompt: Optional[str] = None
    system_header: Optional[str] = None


def load_agent_config(path: Optional[Path] = None) -> AgentConfig:
    """Load agent configuration from a YAML file.

    Args:
        path: Path to the YAML config file. Defaults to the built-in agent.yaml.

    Returns:
        AgentConfig with system_prompt and system_header.

    Raises:
        FileNotFoundError: If the resolved config file does not exist.
    """
    resolved: Path = path or DEFAULT_AGENT_CONFIG

    if not resolved.exists():
        raise FileNotFoundError(f"Agent config file not found: {resolved}")

    with open(resolved) as f:
        data = yaml.safe_load(f) or {}

    return AgentConfig.model_validate(data)


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
