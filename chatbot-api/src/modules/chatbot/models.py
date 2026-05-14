from logging import Logger
from typing import Literal, Optional, List, Any

from google.genai import types
from llama_index.core.base.embeddings.base import BaseEmbedding
from llama_index.core.llms.llm import LLM

from dos_utility.types.models import Provider
from dos_utility.utils.logger import get_logger
from ..env import get_logging_settings, LogSettings

DEFAULT_OLLAMA_URL = "http://localhost:11434"

log_settings: LogSettings = get_logging_settings()
logger: Logger = get_logger(name=__name__, level=log_settings.log_level)


def get_llm(
        provider: Provider,
        model_id: str,
        *,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        request_timeout: Optional[int] = None
) -> LLM:
    """Returns an LLM instance based on the configured provider.

    Args:
        provider: Override the provider from SETTINGS ("google").
        model_id: Override the model ID from SETTINGS.
        temperature: Override the temperature from SETTINGS.
        max_tokens: Override the max tokens from SETTINGS.
        api_key: Override the API key from SETTINGS.
        base_url: Override the base URL from SETTINGS.
        request_timeout: Override the request timeout from SETTINGS.

    Returns:
        LLM: A LlamaIndex-compatible LLM instance.
    """

    params: dict[str, Any] = {
        "temperature": temperature,
        "max_tokens": max_tokens,
        "request_timeout": request_timeout,
    }

    if provider == "google":
        from llama_index.llms.google_genai import GoogleGenAI
        from google.genai.types import (
            GenerateContentConfig,
            HarmCategory,
            HarmBlockThreshold,
            SafetySetting,
        )

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

        if base_url:
            params['http_options'] = types.HttpOptions(base_url=base_url)

        params['generation_config'] = GenerateContentConfig(safety_settings=safety_settings)

        llm: GoogleGenAI = GoogleGenAI(model=model_id,
                                       api_key=api_key,
                                       **{k: v for k, v in params.items() if v is not None})
        logger.debug("LLM loaded - provider=google, model_id=%s", model_id)

    elif provider == "ollama":
        from llama_index.llms.ollama import Ollama

        params['base_url'] = base_url or DEFAULT_OLLAMA_URL

        llm: Ollama = Ollama(model=model_id, **{k: v for k, v in params.items() if v is not None})

        logger.debug("LLM loaded - provider=ollama, model_id=%s, base_url=%s", model_id, base_url)

    return llm


def get_embed_model(
        embed_provider: Provider,
        model_id: str,
        *,
        embed_batch_size: Optional[int] = None,
        embed_dim: Optional[int] = None,
        task_type: Optional[str] = None,
        retries: Optional[int] = None,
        retry_min_seconds: Optional[float] = None,
        api_key: Optional[str] = None,
        embed_base_url: Optional[str] = None
) -> BaseEmbedding:
    """Returns an embedding model instance based on the configured provider.

    Args:
        embed_provider: Override the provider from SETTINGS ("google").
        model_id: Override the embedding model ID from SETTINGS.
        embed_batch_size: Override the batch size from SETTINGS.
        embed_dim: Override the output dimensionality from SETTINGS.
        task_type: Override the embedding task type from SETTINGS.
        retries: Override the number of retries from SETTINGS.
        retry_min_seconds: Override the minimum retry wait time from SETTINGS.
        api_key: Override the API key from SETTINGS.
        embed_base_url: Override the base URL from SETTINGS.

    Returns:
        BaseEmbedding: A LlamaIndex-compatible embedding model instance.
    """
    params: dict[str, Any] = {
        "embed_batch_size": embed_batch_size,
        "retries": retries,
        "retry_min_seconds": retry_min_seconds,
    }

    if embed_provider == "google":
        from llama_index.embeddings.google_genai import GoogleGenAIEmbedding

        http_kwargs = {"base_url": embed_base_url} if embed_base_url else {}
        http_options = types.HttpOptions(**http_kwargs)

        if embed_base_url:
            params['http_options'] = types.HttpOptions(base_url=embed_base_url)

        params['embedding_config'] = types.EmbedContentConfig(
            output_dimensionality=embed_dim,
            task_type=task_type
        )

        embed_model: GoogleGenAIEmbedding = GoogleGenAIEmbedding(model_name=model_id,
                                                                 api_key=api_key,
                                                                 **{k: v for k, v in params.items() if v is not None})

        logger.debug(
            "Embedding model loaded - provider=google, model_id=%s, embed_dim=%s",
            model_id,
            embed_dim,
        )

    elif embed_provider == "ollama":
        from llama_index.embeddings.ollama import OllamaEmbedding

        params['base_url'] = embed_base_url or DEFAULT_OLLAMA_URL

        embed_model: OllamaEmbedding = OllamaEmbedding(model_name=model_id,
                                                       **{k: v for k, v in params.items() if v is not None})

        logger.debug(
            "Embedding model loaded - provider=ollama, model_id=%s",
            model_id
        )

    return embed_model
