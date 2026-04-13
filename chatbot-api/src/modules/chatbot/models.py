from logging import Logger
from typing import overload, Literal, Optional, List
from pydantic import BaseModel
from dos_utility.utils.logger import get_logger
from ..env import get_logging_settings, LogSettings
from google.genai import types
from llama_index.core.llms.llm import LLM
from llama_index.core.base.embeddings.base import BaseEmbedding


log_settings: LogSettings = get_logging_settings()
logger: Logger = get_logger(name=__name__, level=log_settings.log_level)


def get_llm(
        provider: Literal["google"],
        model_id: Optional[str],
        temperature: Optional[float],
        max_tokens: Optional[int],
        api_key: Optional[str],
    ) -> LLM:
    """Returns an LLM instance based on the configured provider.

    Args:
        provider: Override the provider from SETTINGS ("google").
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

    return llm


def get_embed_model(
        provider: Literal["google"],
        model_id: Optional[str],
        embed_batch_size: Optional[int],
        embed_dim: Optional[int],
        task_type: Optional[str],
        retries: Optional[int],
        retry_min_seconds: Optional[float],
        api_key: Optional[str],
    ) -> BaseEmbedding:
    """Returns an embedding model instance based on the configured provider.

    Args:
        provider: Override the provider from SETTINGS ("google").
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

    return embed_model
