from logging import Logger
from functools import lru_cache
from typing import Any, Dict, List, Optional, Self

from dos_utility.utils.logger import get_logger
from dos_utility.agent import (
    AgentConfig,
    AgentInterface,
    AgentResponse,
    ChatGenerationException,
    ChatTurn,
    RagToolSpec,
    get_agent_client,
)

from .tool.loader import load_rag_tool_specs
from .agent import AgentYamlSettings, get_agent_yaml_settings
from .env import ChatbotSettings, get_chatbot_settings
from .structured_outputs import DOS68KAgentOutput
from ..env import LogSettings, get_logging_settings


log_settings: LogSettings = get_logging_settings()
logger: Logger = get_logger(name=__name__, level=log_settings.log_level)


FALLBACK_RESPONSE: str = (
    "Sorry, I could not process your request.\nPlease try rephrasing your question."
)


class Chatbot:
    """Thin orchestrator on top of the provider-agnostic `AgentInterface`.

    Loads tool and agent YAML configurations from `ChatbotSettings`, builds an
    `AgentInterface` instance via `dos_utility.agent.get_agent_client` and
    delegates every chat-generation request to it. The actual LLM provider
    (model, embeddings, reasoning loop, structured output parsing, ...) lives
    entirely inside `dos_utility`, so this module has no direct dependency on
    any LLM SDK.
    """

    def __init__(self: Self):
        self.__settings: ChatbotSettings = get_chatbot_settings()

        agent_yaml: AgentYamlSettings = get_agent_yaml_settings(
            file=self.__settings.agent_config_path
        )
        rag_tools: List[RagToolSpec] = load_rag_tool_specs(
            config_dir=self.__settings.tools_config_dir
        )
        self.tool_names: List[str] = [t.name for t in rag_tools]

        self.agent: AgentInterface = get_agent_client(
            rag_tools=rag_tools,
            agent_config=AgentConfig(
                name=agent_yaml.name,
                description=agent_yaml.description,
                system_prompt=agent_yaml.system_prompt,
                system_header=agent_yaml.system_header,
            ),
            output_schema=DOS68KAgentOutput,
        )

        logger.debug(
            "Chatbot initialized - tools=%s",
            self.tool_names,
        )

    def __messages_to_history(
        self: Self, messages: Optional[List[Dict[str, str]]]
    ) -> List[ChatTurn]:
        if not messages:
            return []

        return [
            ChatTurn(question=m["question"], answer=m.get("answer"))
            for m in messages
        ]

    async def chat_generate(
        self: Self,
        query_str: str,
        messages: Optional[List[Dict[str, str]]] = None,
    ) -> Dict[str, Any]:
        """Generate a response for `query_str` and return it as a plain dict.

        Args:
            query_str: The user's current question.
            messages: Chat history shaped as a list of `{"question", "answer"}` dicts,
                ordered oldest first.

        Returns:
            Dict with keys: `response`, `tags`, `context`. On failure a safe
            fallback payload with `FALLBACK_RESPONSE` is returned instead.
        """
        history: List[ChatTurn] = self.__messages_to_history(messages=messages)
        logger.debug("Converted chat history, %d turns", len(history))

        try:
            response: AgentResponse = await self.agent.chat_generate(
                query=query_str, history=history
            )

            return {
                "response": response.response,
                "tags": response.tags,
                "context": [c.model_dump() for c in response.context],
            }
        except ChatGenerationException as e:
            logger.warning("Chat generation failed: %s", e)
        except Exception as e:
            logger.warning(f"Exception: {e}")

        return {
            "response": FALLBACK_RESPONSE,
            "tags": [],
            "context": [],
        }


@lru_cache
def get_chatbot() -> Chatbot:
    return Chatbot()
