from logging import Logger
from typing import overload, Literal, Optional, Any, Sequence, Type, Self, List
from pydantic import BaseModel
from dos_utility.utils.logger import get_logger
from ..env import get_logging_settings, LogSettings
from google.genai import types
from llama_index.core.llms.llm import LLM
from llama_index.core.base.embeddings.base import BaseEmbedding
from llama_index.core.llms import MockLLM
from llama_index.core.llms import CompletionResponse, ChatResponse, ChatMessage, MessageRole


# ---------------------------------------------------------------------------
# Mock LLM — returns valid ReAct format for agent reasoning steps and valid
# JSON for structured output extraction, so the full pipeline can be tested
# without a real LLM provider.
# ---------------------------------------------------------------------------

_REACT_TEXT = (
    "Thought: I have enough context to answer the question.\n"
    "Answer: Mock response for testing purposes."
)
_JSON_TEXT = '{"response": "Mock response for testing purposes."}'


log_settings: LogSettings = get_logging_settings()
logger: Logger = get_logger(name=__name__, level=log_settings.log_level)


class _JsonMockLLM(MockLLM):
    """Inner mock used inside StructuredLLM — always returns valid JSON."""

    def complete(self: Self, prompt: str, **kwargs: Any) -> CompletionResponse:
        return CompletionResponse(text=_JSON_TEXT)

    async def acomplete(self: Self, prompt: str, **kwargs: Any) -> CompletionResponse:
        return CompletionResponse(text=_JSON_TEXT)


class _MockLLM(MockLLM):
    """Mock LLM that produces valid ReAct responses and delegates structured
    output to a JSON-returning inner mock so parsing never fails."""

    def complete(self: Self, prompt: str, **kwargs: Any) -> CompletionResponse:
        return CompletionResponse(text=_REACT_TEXT)

    async def acomplete(self: Self, prompt: str, **kwargs: Any) -> CompletionResponse:
        return CompletionResponse(text=_REACT_TEXT)

    def chat(self: Self, messages: Sequence[ChatMessage], **kwargs: Any) -> ChatResponse:
        return ChatResponse(
            message=ChatMessage(role=MessageRole.ASSISTANT, content=_REACT_TEXT)
        )

    async def achat(self: Self, messages: Sequence[ChatMessage], **kwargs: Any) -> ChatResponse:
        return ChatResponse(
            message=ChatMessage(role=MessageRole.ASSISTANT, content=_REACT_TEXT)
        )

    def as_structured_llm(self: Self, output_cls: Type[BaseModel], **kwargs: Any):
        from llama_index.core.llms.structured_llm import StructuredLLM

        return StructuredLLM(llm=_JsonMockLLM(max_tokens=256), output_cls=output_cls, **kwargs)


@overload
def get_llm(provider: Literal["mock"]) -> LLM: ...

@overload
def get_llm(
        provider: Literal["google"],
        model_id: str,
        temperature: float,
        max_tokens: int,
        api_key: str,
    ) -> LLM:
    ...

def get_llm(
        provider: Literal["google", "mock"],
        model_id: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        api_key: Optional[str] = None,
    ) -> LLM:
    """Returns an LLM instance based on the configured provider.

    Args:
        provider: Override the provider from SETTINGS ("google" | "mock").
        model_id: Override the model ID from SETTINGS.
        temperature: Override the temperature from SETTINGS.
        max_tokens: Override the max tokens from SETTINGS.

    Returns:
        LLM: A LlamaIndex-compatible LLM instance.
    """
    if provider == "google":
        from llama_index.llms.google_genai import GoogleGenAI
        from google.genai.types import GenerateContentConfig, HarmCategory, HarmBlockThreshold, SafetySetting

        safety_settings: List[SafetySetting] = [
            SafetySetting(
                category=HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                threshold=HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
            ),
            SafetySetting(
                category=HarmCategory.HARM_CATEGORY_HARASSMENT,
                threshold=HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
            ),
            SafetySetting(
                category=HarmCategory.HARM_CATEGORY_HATE_SPEECH,
                threshold=HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
            ),
            SafetySetting(
                category=HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
                threshold=HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
            ),
        ]
        llm: GoogleGenAI = GoogleGenAI(
            model=model_id,
            temperature=temperature,
            max_tokens=max_tokens,
            api_key=api_key,
            generation_config=GenerateContentConfig(safety_settings=safety_settings),
        )
        logger.debug("LLM loaded - provider=google, model_id=%s", model_id)
    elif provider == "mock":
        llm = _MockLLM(max_tokens=256)
        logger.debug("LLM loaded - provider=mock")

    return llm


@overload
def get_embed_model(provider: Literal["mock"], embed_dim: int) -> BaseEmbedding: ...

@overload
def get_embed_model(
        provider: Literal["google"],
        model_id: str,
        embed_batch_size: int,
        embed_dim: int,
        task_type: str,
        retries: int,
        retry_min_seconds: float,
        api_key: str,
    ) -> BaseEmbedding:
    ...

def get_embed_model(
        provider: Literal["google", "mock"],
        model_id: Optional[str] = None,
        embed_batch_size: Optional[int] = None,
        embed_dim: Optional[int] = None,
        task_type: Optional[str] = None,
        retries: Optional[int] = None,
        retry_min_seconds: Optional[float] = None,
        api_key: Optional[str] = None,
    ) -> BaseEmbedding:
    """Returns an embedding model instance based on the configured provider.

    Args:
        provider: Override the provider from SETTINGS ("google" | "mock").
        model_id: Override the embedding model ID from SETTINGS.
        embed_batch_size: Override the batch size from SETTINGS.
        embed_dim: Override the output dimensionality from SETTINGS.
        task_type: Override the embedding task type from SETTINGS.
        retries: Override the number of retries from SETTINGS.
        retry_min_seconds: Override the minimum retry wait time from SETTINGS.

    Returns:
        BaseEmbedding: A LlamaIndex-compatible embedding model instance.
    """
    if provider == "google":
        from llama_index.embeddings.google_genai import GoogleGenAIEmbedding

        embed_model = GoogleGenAIEmbedding(
            model_name=model_id,
            api_key=api_key,
            embed_batch_size=embed_batch_size,
            retries=retries,
            retry_min_seconds=retry_min_seconds,
            embedding_config=types.EmbedContentConfig(
                output_dimensionality=embed_dim,
                task_type=task_type,
            ),
        )
        logger.debug("Embedding model loaded - provider=google, model_id=%s, embed_dim=%s", model_id, embed_dim)

    elif provider == "mock":
        from llama_index.core import MockEmbedding

        embed_model = MockEmbedding(embed_dim=embed_dim)
        logger.debug("Embedding model loaded - provider=mock, embed_dim=%s", embed_dim)

    return embed_model
