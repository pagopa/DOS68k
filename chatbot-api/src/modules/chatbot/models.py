from google.genai import types

from llama_index.core.llms.llm import LLM
from llama_index.core.base.embeddings.base import BaseEmbedding

from dos_utility.utils.logger import get_logger

from src.modules.settings import SETTINGS


LOGGER = get_logger(__name__, level=SETTINGS.log_level)


def get_llm(
    provider: str | None = None,
    model_id: str | None = None,
    temperature: float | None = None,
    max_tokens: int | None = None,
) -> LLM:
    """Returns an LLM instance based on the configured provider.

    Args:
        provider: Override the provider from SETTINGS ("google" | "mock").
        model_id: Override the model ID from SETTINGS.
        temperature: Override the temperature from SETTINGS.
        max_tokens: Override the max tokens from SETTINGS.

    Returns:
        LLM: A LlamaIndex-compatible LLM instance.

    Raises:
        AssertionError: If provider is not "google" or "mock".
    """
    provider = provider or SETTINGS.provider
    model_id = model_id or SETTINGS.model_id
    temperature = temperature or SETTINGS.temperature_rag
    max_tokens = max_tokens or SETTINGS.max_tokens

    if provider == "google":
        from llama_index.llms.google_genai import GoogleGenAI

        llm = GoogleGenAI(
            model=model_id,
            temperature=temperature,
            max_tokens=max_tokens,
            api_key=SETTINGS.google_api_key,
        )
        LOGGER.info(f"{model_id} LLM loaded successfully from Google!")

    elif provider == "mock":
        from llama_index.core.llms import MockLLM

        llm = MockLLM(max_tokens=5)
        LOGGER.info("Mock LLM loaded successfully!")

    else:
        raise AssertionError(f"Provider must be 'google' or 'mock'. Given: {provider}.")

    return llm


def get_embed_model(
    provider: str | None = None,
    model_id: str | None = None,
    embed_batch_size: int | None = None,
    embed_dim: int | None = None,
    task_type: str | None = None,
    retries: int | None = None,
    retry_min_seconds: float | None = None,
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

    Raises:
        AssertionError: If provider is not "google" or "mock".
    """
    provider = provider or SETTINGS.provider
    model_id = model_id or SETTINGS.embed_model_id
    embed_batch_size = embed_batch_size or SETTINGS.embed_batch_size
    embed_dim = embed_dim or SETTINGS.embed_dim
    task_type = task_type or SETTINGS.embed_task
    retries = retries or SETTINGS.embed_retries
    retry_min_seconds = retry_min_seconds or SETTINGS.embed_retry_min_seconds

    if provider == "google":
        from llama_index.embeddings.google_genai import GoogleGenAIEmbedding

        embed_model = GoogleGenAIEmbedding(
            model_name=model_id,
            api_key=SETTINGS.google_api_key,
            embed_batch_size=embed_batch_size,
            retries=retries,
            retry_min_seconds=retry_min_seconds,
            embedding_config=types.EmbedContentConfig(
                output_dimensionality=embed_dim,
                task_type=task_type,
            ),
        )
        LOGGER.info(f"{model_id} embedding model loaded successfully from Google!")

    elif provider == "mock":
        from llama_index.core import MockEmbedding

        embed_model = MockEmbedding(embed_dim=embed_dim)
        LOGGER.info("Mock embedding model loaded successfully!")

    else:
        raise AssertionError(f"Provider must be 'google' or 'mock'. Given: {provider}.")

    return embed_model
