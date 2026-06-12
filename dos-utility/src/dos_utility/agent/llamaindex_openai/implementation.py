from logging import Logger
from typing import Any, Dict, List, Optional, Self, Type

from pydantic import BaseModel
from workflows import Context
from llama_index.core.agent.workflow import AgentOutput, ReActAgent
from llama_index.core.base.embeddings.base import BaseEmbedding
from llama_index.core.llms import ChatMessage, MessageRole
from llama_index.core.llms.llm import LLM, ToolSelection

from ..interface import AgentInterface
from ..models import AgentConfig, AgentResponse, ChatTurn, ContextChunk, RagToolSpec
from ..exceptions import AgentInitializationException, ChatGenerationException
from ...utils.logger import get_logger
from .env import LlamaIndexOpenAIAgentSettings, get_llamaindex_openai_agent_settings
from ._models import get_embed_model, get_llm
from ._tools import build_rag_tools
from ._agent import build_react_agent


logger: Logger = get_logger(name=__name__)


class LlamaIndexOpenAIAgent(AgentInterface):
    """`AgentInterface` implementation backed by LlamaIndex ReActAgent + OpenAI.

    The whole LlamaIndex / OpenAI surface is contained in this provider:
    callers see only `AgentInterface` and the data models exported from
    :mod:`dos_utility.agent`.
    """

    def __init__(
        self: Self,
        *,
        rag_tools: List[RagToolSpec],
        agent_config: AgentConfig,
        output_schema: Optional[Type[BaseModel]] = None,
    ) -> None:
        try:
            self._settings: LlamaIndexOpenAIAgentSettings = (
                get_llamaindex_openai_agent_settings()
            )

            self._llm: LLM = get_llm(
                model_id=self._settings.MODEL_ID,
                api_key=self._settings.MODEL_API_KEY.get_secret_value(),
                temperature=self._settings.TEMPERATURE_AGENT,
                max_tokens=self._settings.MAX_TOKENS,
                api_base=self._settings.OPENAI_API_BASE,
            )
            self._embed_model: BaseEmbedding = get_embed_model(
                model_id=self._settings.EMBED_MODEL_ID,
                api_key=self._settings.MODEL_API_KEY.get_secret_value(),
                embed_dim=self._settings.EMBED_DIM,
                embed_batch_size=self._settings.EMBED_BATCH_SIZE,
                retries=self._settings.EMBED_RETRIES,
                api_base=self._settings.OPENAI_API_BASE,
            )

            tools = build_rag_tools(
                rag_tools=rag_tools,
                llm=self._llm,
                embed_model=self._embed_model,
                default_similarity_top_k=self._settings.SIMILARITY_TOPK,
            )
            self._tool_names: List[str] = [spec.name for spec in rag_tools]
            self._agent: ReActAgent = build_react_agent(
                llm=self._llm,
                tools=tools,
                name=agent_config.name,
                description=agent_config.description,
                system_prompt=agent_config.system_prompt,
                system_header=agent_config.system_header,
                output_cls=output_schema,
            )

            logger.debug(
                "LlamaIndexOpenAIAgent initialized - model_id=%s, tools=%s",
                self._settings.MODEL_ID,
                self._tool_names,
            )
        except Exception as e:
            raise AgentInitializationException(msg=str(e))

    async def is_healthy(self: Self) -> bool:
        try:
            await self._llm.acomplete("ping")
            return True
        except Exception as e:
            logger.warning("LlamaIndexOpenAIAgent health check failed: %s", e)
            return False

    async def close(self: Self) -> None:
        # The OpenAI client does not currently require explicit cleanup.
        return None

    def _history_to_chat_messages(
        self: Self, history: Optional[List[ChatTurn]]
    ) -> List[ChatMessage]:
        msgs: List[ChatMessage] = []

        if not history:
            return msgs

        for turn in history:
            msgs.append(ChatMessage(role=MessageRole.USER, content=turn.question))
            if turn.answer is not None:
                msgs.append(
                    ChatMessage(
                        role=MessageRole.ASSISTANT, content=turn.answer.strip()
                    )
                )

        return msgs

    def _context_from_tool_calls(
        self: Self, tool_calls: List[ToolSelection]
    ) -> List[ContextChunk]:
        chunks: List[ContextChunk] = []

        for call in tool_calls:
            nodes = getattr(call.tool_output.raw_output, "source_nodes", [])
            for node in nodes:
                chunks.append(
                    ContextChunk(
                        filename=node.metadata.get("filename", ""),
                        chunk_id=int(node.metadata.get("chunk_id", 0) or 0),
                        content=node.text,
                        score=node.score,
                    )
                )

        chunks.sort(key=lambda c: (c.score is None, -(c.score or 0)))
        return chunks

    async def chat_generate(
        self: Self,
        query: str,
        history: Optional[List[ChatTurn]] = None,
    ) -> AgentResponse:
        chat_history: List[ChatMessage] = self._history_to_chat_messages(
            history=history
        )
        logger.debug("Converted chat history, %d messages", len(chat_history))

        try:
            ctx: Context = Context.from_dict(workflow=self._agent, data={})

            logger.debug("Running agent...")
            engine_response: AgentOutput = await self._agent.run(
                user_msg=query,
                chat_history=chat_history,
                ctx=ctx,
                early_stopping_method="generate",
            )
            logger.debug("Agent run completed")
        except Exception as e:
            raise ChatGenerationException(msg=str(e))

        structured: Optional[Dict[str, Any]] = engine_response.structured_response

        if not isinstance(structured, dict) or "response" not in structured:
            raise ChatGenerationException(
                msg=f"Structured output parsing failed (got type={type(structured).__name__})"
            )

        return AgentResponse(
            response=structured["response"],
            tags=[],
            context=self._context_from_tool_calls(
                tool_calls=engine_response.tool_calls
            ),
        )


def get_llamaindex_openai_agent(
    *,
    rag_tools: List[RagToolSpec],
    agent_config: AgentConfig,
    output_schema: Optional[Type[BaseModel]] = None,
) -> LlamaIndexOpenAIAgent:
    return LlamaIndexOpenAIAgent(
        rag_tools=rag_tools,
        agent_config=agent_config,
        output_schema=output_schema,
    )
