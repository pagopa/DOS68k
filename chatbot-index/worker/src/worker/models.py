from logging import Logger
from typing import overload, Literal, Optional
from google.genai import types
from llama_index.core.base.embeddings.base import BaseEmbedding

# from dos_utility.utils.logger import get_logger
# from ..env import get_logging_settings, LogSettings
# log_settings: LogSettings = get_logging_settings()
# logger: Logger = get_logger(name=__name__, level=log_settings.log_level)


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
        # logger.debug("Embedding model loaded - provider=google, model_id=%s, embed_dim=%s", model_id, embed_dim)

    return embed_model
