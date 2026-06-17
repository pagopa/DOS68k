from typing import Any, Callable, Dict, List, Optional, Type

from llama_index.core.agent.workflow import ReActAgent
from llama_index.core.llms.llm import LLM
from llama_index.core.tools import BaseTool


def build_react_agent(
    *,
    llm: LLM,
    tools: List[BaseTool | Callable],
    name: Optional[str] = None,
    description: Optional[str] = None,
    system_prompt: Optional[str] = None,
    system_header: Optional[str] = None,
    output_cls: Optional[Type] = None,
) -> ReActAgent:
    """Create and configure a LlamaIndex ReActAgent instance."""
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
