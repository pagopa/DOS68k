from logging import Logger
from functools import lru_cache
from typing import Optional, List, Dict, Self
from workflows import Context
from llama_index.core.tools import QueryEngineTool
from llama_index.core.llms import ChatMessage, MessageRole
from llama_index.core.llms.llm import LLM
from llama_index.core.base.embeddings.base import BaseEmbedding
from llama_index.core.agent.workflow import AgentOutput as LlamaAgentOutput, ReActAgent
from dos_utility.utils.logger import get_logger

from .models import get_llm, get_embed_model
from .tool.loader import load_tools
from .agent import get_agent, get_agent_yaml_settings, AgentYamlSettings
from .env import get_chatbot_settings, ChatbotSettings
from .structured_outputs import AgentOutput
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
            use_async=self.__settings.use_async,
            config_dir=self.__settings.tools_config_dir,
        )
        self.tool_names: List[str] = list(tools_map.keys())
        logger.debug(
            "Chatbot initialized - provider=%s, model_id=%s, tools=%s",
            self.__settings.provider, self.__settings.model_id, self.tool_names,
        )

        agent_config: AgentYamlSettings = get_agent_yaml_settings(file=self.__settings.agent_config_path)
        self.agent: ReActAgent = get_agent(
            name=agent_config.name,
            description=agent_config.description,
            llm=self.model,
            system_prompt=agent_config.system_prompt,
            output_cls=AgentOutput,
            system_header=agent_config.system_header,
            tools=list(tools_map.values()),
        )

    def __extract_references(self: Self, tool_calls: list) -> List[dict]:
        """Derives source references from the retrieved nodes of all tool calls.

        Deduplicates by source filename so each document appears once.

        Args:
            tool_calls: List of ToolCallResult objects from the agent response.

        Returns:
            List of dicts with key 'source' (the document filename).
        """
        seen: set = set()
        refs: List[dict] = []

        logger.debug("Extracting references from %d tool call(s)", len(tool_calls))
        for tool_call in tool_calls:
            nodes = getattr(tool_call.tool_output.raw_output, "source_nodes", [])
            for node in nodes:
                source = node.metadata.get("filename")
                if source and source not in seen:
                    seen.add(source)
                    refs.append({"source": source})

        logger.debug("Extracted %d unique reference(s): %s", len(refs), [r["source"] for r in refs])
        return refs

    def __extract_contexts(self: Self, tool_calls: list) -> List[str]:
        """Collects the retrieved document chunks from all tool calls.

        Each RAG tool call attaches source nodes to its raw output. This method
        walks all calls and formats each node as a labelled text block.

        Args:
            tool_calls: List of ToolCallResult objects from the agent response.

        Returns:
            List of formatted context strings, one per source node.
        """
        contexts = []

        for tool_call in tool_calls:
            nodes = getattr(tool_call.tool_output.raw_output, "source_nodes", [])
            logger.debug(
                "Tool call %s returned %d chunk(s): %s",
                getattr(tool_call, "tool_name", "unknown"),
                len(nodes),
                [(n.metadata.get("filename", "?"), n.metadata.get("chunk_id", "?")) for n in nodes],
            )
            contexts.extend(
                f"-------\nFile: {node.metadata.get('filename', 'unknown')} "
                f"(chunk {node.metadata.get('chunk_id', '?')})\n\n{node.text}\n\n"
                for node in nodes
            )

        return contexts

    def __get_response_json(self: Self, engine_response: LlamaAgentOutput) -> dict:
        """Converts the agent's raw output into the API response dict.

        Args:
            engine_response: The AgentOutput returned by agent.run(). Its
                structured_response field holds the validated AgentOutput Pydantic
                model as a dict when parsing succeeded, or a non-dict value on failure.

        Returns:
            Dict with keys: response, tags, references, contexts.
        """
        structured = engine_response.structured_response

        if not isinstance(structured, dict):
            logger.debug("Structured output parsing failed - got type=%s, falling back to error response", type(structured).__name__)
            # Structured output parsing failed — return a safe fallback.
            return {
                "response": "Sorry, I could not process your request.\nPlease try rephrasing your question.",
                "tags": [],
                "references": [],
                "contexts": [],
            }

        logger.debug("Structured output parsed successfully - tool_calls=%d", len(engine_response.tool_calls))
        return {
            "response": structured["response"],
            "tags": structured.get("tags", []),
            "references": self.__extract_references(engine_response.tool_calls),
            "contexts": self.__extract_contexts(engine_response.tool_calls),
        }

    def __messages_to_chathistory(self: Self, messages: Optional[List[Dict[str, str]]] = None) -> List[ChatMessage]:
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
                chat_history.append(ChatMessage(role=MessageRole.USER, content=user_content))

                if assistant_content is not None:
                    chat_history.append(ChatMessage(role=MessageRole.ASSISTANT, content=assistant_content))

        return chat_history

    async def chat_generate(
            self: Self,
            query_str: str,
            messages: Optional[List[Dict[str, str]]] = None,
            knowledge_base: Optional[str] = None,
        ) -> dict:
        """Generates a response to the user's query.

        Args:
            query_str: The user's query string.
            messages: Chat history. Each dict has "question" and "answer" keys.
            knowledge_base: Optional knowledge base identifier appended to the query
                to hint the agent toward a specific tool.

        Returns:
            Dict with keys: response, tags, references, contexts.
        """
        chat_history: List[ChatMessage] = self.__messages_to_chathistory(messages=messages)
        logger.debug("chat_generate - query=%r, knowledge_base=%s, chat_history_length=%d", query_str, knowledge_base, len(chat_history))

        if knowledge_base is not None:
            query_str = query_str + f" | Knowledge Base: {knowledge_base}"
            logger.debug("Query with KB hint: %r", query_str)

        try:
            ctx: Context = Context.from_dict(workflow=self.agent, data={})
            logger.debug("Running agent...")
            engine_response = await self.agent.run(
                user_msg=query_str,
                chat_history=chat_history,
                ctx=ctx,
                early_stopping_method="generate",
            )
            logger.debug("Agent run completed - response type=%s", type(engine_response).__name__)
            response_json = self.__get_response_json(engine_response=engine_response)
        except Exception as e:
            response_json = {
                "response": "Sorry, I could not process your request.\nPlease try rephrasing your question.",
                "tags": [],
                "references": [],
                "contexts": [],
            }
            logger.warning(f"Exception: {e}")

        return response_json


@lru_cache
def get_chatbot() -> Chatbot:
    return Chatbot()
