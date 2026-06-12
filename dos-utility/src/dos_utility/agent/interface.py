from abc import ABC, abstractmethod
from typing import List, Optional, Self

from .models import AgentResponse, ChatTurn


class AgentInterface(ABC):
    """Adaptive layer for LLM-backed agent interactions.

    Concrete implementations encapsulate every detail of the underlying
    LLM provider (model selection, embeddings, tool wiring, the reasoning
    loop, structured-output parsing, ...). Consumers interact exclusively
    through this interface and the data models in
    :mod:`dos_utility.agent.models`, so the calling service stays free of
    any provider-specific SDK dependency.
    """

    @abstractmethod
    async def is_healthy(self: Self) -> bool:
        """Check whether the underlying LLM provider is reachable.

        If the implementation could raise an exception when not healthy, it
        should be caught and `False` returned.

        Returns:
            bool: True if healthy, False otherwise.
        """
        ...

    @abstractmethod
    async def chat_generate(
        self: Self,
        query: str,
        history: Optional[List[ChatTurn]] = None,
    ) -> AgentResponse:
        """Generate a response to the user's query.

        Args:
            query (str): The current user question.
            history (Optional[List[ChatTurn]]): Prior conversation turns, ordered
                oldest first. May be omitted for a fresh conversation.

        Returns:
            AgentResponse: Structured response with the final answer, retrieved
                context chunks and any topic tags.

        Raises:
            ChatGenerationException: When the provider fails to produce a valid
                structured response.

        Examples:
            >>> agent = get_agent_client(rag_tools=[...], agent_config=AgentConfig(...))
            >>> response: AgentResponse = await agent.chat_generate(
            >>>     query="What is the project about?",
            >>>     history=[ChatTurn(question="Hi", answer="Hello!")],
            >>> )
        """
        ...

    @abstractmethod
    async def close(self: Self) -> None:
        """Release any provider-side resources held by this agent.

        Idempotent: calling `close` multiple times must be a no-op. Intended
        to be invoked once on graceful shutdown (e.g. from a FastAPI
        lifespan handler).
        """
        ...
