from llama_index.core.tools import BaseTool
from llama_index.core.llms.llm import LLM
from llama_index.core.agent.workflow import ReActAgent
from typing import Callable

from src.modules.chatbot.models import get_llm
from src.modules.chatbot.structured_outputs import DiscoveryOutput
from src.modules.settings import SETTINGS


DISCOVERY_AGENT_NAME = "DiscoveryAgent"
DEFAULT_DESCRIPTION = (
    "This agent is designed to answer questions about the world and perform actions using tools. "
    "It uses a ReAct reasoning process to determine the best course of action based on the input question and the available tools."
)


def get_discovery_agent(
    description: str | None = None,
    tools: list[BaseTool | Callable] | None = None,
    llm: LLM | None = None,
) -> ReActAgent:
    """Create and configure a ReActAgent instance.

    Args:
        description: Optional description of the agent's role. Defaults to DEFAULT_DESCRIPTION.
        tools: Optional list of tools the agent can use.
        llm: Optional LLM override. Defaults to get_llm(temperature_agent).

    Returns:
        ReActAgent: The configured discovery agent.
    """
    description = description or DEFAULT_DESCRIPTION
    llm = llm or get_llm(temperature=SETTINGS.temperature_agent)

    agent = ReActAgent(
        name=DISCOVERY_AGENT_NAME,
        description=description,
        system_prompt=SETTINGS.discovery_system_prompt_str,
        tools=tools,
        llm=llm,
        output_cls=DiscoveryOutput,
    )

    agent.formatter.system_header = SETTINGS.react_system_str

    return agent
