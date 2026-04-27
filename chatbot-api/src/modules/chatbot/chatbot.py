from logging import Logger
from functools import lru_cache
from typing import Optional, List, Dict, Self, Any
from workflows import Context
from llama_index.core.tools import QueryEngineTool
from llama_index.core.llms import ChatMessage, MessageRole
from llama_index.core.llms.llm import LLM, ToolSelection
from llama_index.core.base.embeddings.base import BaseEmbedding
from llama_index.core.agent.workflow import AgentOutput, ReActAgent
from dos_utility.utils.logger import get_logger

from .models import get_llm, get_embed_model
from .tool.loader import load_tools
from .agent import get_agent, get_agent_yaml_settings, AgentYamlSettings
from .env import get_chatbot_settings, ChatbotSettings
from .structured_outputs import DOS68KAgentOutput
from ..env import get_logging_settings, LogSettings


log_settings: LogSettings = get_logging_settings()
logger: Logger = get_logger(name=__name__, level=log_settings.log_level)


class Chatbot:
    """RAG-based chatbot backed by a ReActAgent and one or more query engine tools.

    Tools are loaded from YAML configs at startup (see tool/loader.py).
    Agent behaviour (system prompt) is loaded from a YAML config (see agent.yaml).
    A single LLM instance is used for both RAG synthesis and agent reasoning,
    tuned via temperature_agent.
    """

    def __init__(self: Self):
        self.__settings: ChatbotSettings = get_chatbot_settings()

        # LLM for agent reasoning and RAG synthesis.
        self.model: LLM = get_llm(
            provider=self.__settings.provider,
            model_id=self.__settings.model_id,
            temperature=self.__settings.temperature_agent,
            max_tokens=self.__settings.max_tokens,
            api_key=self.__settings.model_api_key,
        )
        self.embed_model: BaseEmbedding = get_embed_model(
            provider=self.__settings.provider,
            model_id=self.__settings.embed_model_id,
            embed_batch_size=self.__settings.embed_batch_size,
            embed_dim=self.__settings.embed_dim,
            task_type=self.__settings.embed_task,
            retries=self.__settings.embed_retries,
            retry_min_seconds=self.__settings.embed_retry_min_seconds,
            api_key=self.__settings.model_api_key,
        )
        # Load all tools from YAML configs. Each tool wraps a vector index.
        tools_map: Dict[str, QueryEngineTool] = load_tools(
            llm=self.model,
            embed_model=self.embed_model,
            similarity_top_k=self.__settings.similarity_topk,
            config_dir=self.__settings.tools_config_dir,
        )
        self.tool_names: List[str] = list(tools_map.keys())
        logger.debug(
            "Chatbot initialized - provider=%s, model_id=%s, tools=%s",
            self.__settings.provider,
            self.__settings.model_id,
            self.tool_names,
        )

        agent_config: AgentYamlSettings = get_agent_yaml_settings(
            file=self.__settings.agent_config_path
        )
        self.agent: ReActAgent = get_agent(
            name=agent_config.name,
            description=agent_config.description,
            llm=self.model,
            system_prompt=agent_config.system_prompt,
            output_cls=DOS68KAgentOutput,
            system_header=agent_config.system_header,
            tools=list(tools_map.values()),
        )

    def __get_context(
        self: Self, tool_calls: List[ToolSelection]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Retrieve context for the answer, if any RAG tool has been called.

        Args:
            tool_calls (List[ToolSelection]): tool called

        Returns:
            Dict[str, Dict[str, Any]]: for each file (saved in the vector db), it returns the retrieved chunk.
                                        Example: {
                                            "file1": [
                                                {
                                                    "chunk_id": 1,
                                                    "content": "some content",
                                                    "score": 0.9,
                                                },
                                            ],
                                            ...
                                        }
        """
        context: Dict[str, List[Dict[str, Any]]] = {}

        for tool_call in tool_calls:
            nodes = getattr(tool_call.tool_output.raw_output, "source_nodes", [])
            for node in nodes:
                filename: str = node.metadata.get("filename", "")
                chunk_id: str = node.metadata.get("chunk_id", "")
                score: Optional[float] = node.metadata.get("score", None)
                content: str = node.text

                # Create empty if not exists
                if filename not in context.keys():
                    context[filename] = []

                # Add new chunk
                context[filename].append(
                    {
                        "chunk_id": chunk_id,
                        "content": content,
                        "score": score,
                    }
                )

        return context

    def __get_response_json(self: Self, engine_response: AgentOutput) -> Dict[str, Any]:
        """Converts the agent's raw output into the API response dict.

        Args:
            engine_response: The AgentOutput returned by agent.run(). Its
                structured_response field holds the validated AgentOutput Pydantic
                model as a dict when parsing succeeded, or a non-dict value on failure.

        Returns:
            Dict with keys: response, tags, contexts.
        """
        structured: Optional[Dict[str, Any]] = (
            engine_response.structured_response
        )  # This is the DOS68KAgentOutput class

        if not isinstance(structured, dict):
            logger.debug(
                "Structured output parsing failed - got type=%s, falling back to error response",
                type(structured).__name__,
            )
            # Structured output parsing failed — return a safe fallback.
            return {
                "response": "Sorry, I could not process your request.\nPlease try rephrasing your question.",
                "tags": [],
                "context": [],
            }

        logger.debug(
            "Structured output parsed successfully - tool_calls=%d",
            len(engine_response.tool_calls),
        )
        return {
            "response": structured["response"],
            "tags": [],  # Left missing for now
            "context": self.__get_context(tool_calls=engine_response.tool_calls),
        }

    def __messages_to_chathistory(
        self: Self, messages: Optional[List[Dict[str, str]]] = None
    ) -> List[ChatMessage]:
        """Converts the API chat history format into LlamaIndex ChatMessage objects.

        Args:
            messages: List of dicts with "question" and "answer" keys, ordered oldest first.
                The "answer" value may be None for the last turn if the assistant hasn't replied yet.

        Returns:
            Flat list of alternating USER / ASSISTANT ChatMessage objects.
        """
        chat_history: List[ChatMessage] = []

        if messages is not None:
            for message in messages:
                user_content: str = message["question"]
                assistant_content: Optional[str] = (
                    message["answer"].strip()
                    if message.get("answer") is not None
                    else None
                )
                chat_history.append(
                    ChatMessage(role=MessageRole.USER, content=user_content)
                )

                if assistant_content is not None:
                    chat_history.append(
                        ChatMessage(
                            role=MessageRole.ASSISTANT, content=assistant_content
                        )
                    )

        return chat_history

    async def chat_generate(
        self: Self,
        query_str: str,
        messages: Optional[List[Dict[str, str]]] = None,
    ) -> Dict[str, Any]:
        """Generates a response to the user's query.

        Args:
            query_str: The user's query string.
            messages: Chat history. Each dict has "question" and "answer" keys.

        Returns:
            Dict with keys: response, tags, references, contexts.
        """
        chat_history: List[ChatMessage] = self.__messages_to_chathistory(
            messages=messages
        )
        logger.debug(
            "chat_generate - query=%r, chat_history_length=%d",
            query_str,
            len(chat_history),
        )

        try:
            ctx: Context = Context.from_dict(workflow=self.agent, data={})
            logger.debug("Running agent...")
            engine_response: AgentOutput = await self.agent.run(
                user_msg=query_str,
                chat_history=chat_history,
                ctx=ctx,
                early_stopping_method="generate",
            )
            logger.debug(
                "Agent run completed - response type=%s", type(engine_response).__name__
            )
            response_json: Dict[str, Any] = self.__get_response_json(
                engine_response=engine_response
            )
        except Exception as e:
            response_json = {
                "response": "Sorry, I could not process your request.\nPlease try rephrasing your question.",
                "tags": [],
                "context": [],
            }
            logger.warning(f"Exception: {e}")

        return response_json


@lru_cache
def get_chatbot() -> Chatbot:
    return Chatbot()
