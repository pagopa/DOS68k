from typing import Optional

from llama_index.core.llms.llm import LLM
from llama_index.core.base.embeddings.base import BaseEmbedding
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding


def get_llm(
    model_id: str,
    api_key: str,
    temperature: float,
    max_tokens: int,
    api_base: Optional[str] = None,
) -> LLM:
    """Build a LlamaIndex-compatible LLM backed by OpenAI."""
    kwargs = {
        "model": model_id,
        "api_key": api_key,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    if api_base is not None:
        kwargs["api_base"] = api_base

    return OpenAI(**kwargs)


def get_embed_model(
    model_id: str,
    api_key: str,
    embed_dim: int,
    embed_batch_size: int,
    retries: int,
    api_base: Optional[str] = None,
) -> BaseEmbedding:
    """Build a LlamaIndex-compatible embedding model backed by OpenAI."""
    kwargs = {
        "model": model_id,
        "api_key": api_key,
        "embed_batch_size": embed_batch_size,
        "dimensions": embed_dim,
        "max_retries": retries,
    }
    if api_base is not None:
        kwargs["api_base"] = api_base

    return OpenAIEmbedding(**kwargs)
