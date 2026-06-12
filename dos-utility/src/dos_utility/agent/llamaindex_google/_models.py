from llama_index.core.llms.llm import LLM
from llama_index.core.base.embeddings.base import BaseEmbedding
from llama_index.llms.google_genai import GoogleGenAI
from llama_index.embeddings.google_genai import GoogleGenAIEmbedding
from google.genai import types
from google.genai.types import (
    GenerateContentConfig,
    HarmCategory,
    HarmBlockThreshold,
    SafetySetting,
)


def get_llm(
    model_id: str,
    api_key: str,
    temperature: float,
    max_tokens: int,
) -> LLM:
    """Build a LlamaIndex-compatible LLM backed by Google GenAI."""
    safety_settings = [
        SafetySetting(
            category=cat,
            threshold=HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
        )
        for cat in (
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
            HarmCategory.HARM_CATEGORY_HARASSMENT,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
        )
    ]

    return GoogleGenAI(
        model=model_id,
        temperature=temperature,
        max_tokens=max_tokens,
        api_key=api_key,
        generation_config=GenerateContentConfig(safety_settings=safety_settings),
    )


def get_embed_model(
    model_id: str,
    api_key: str,
    embed_dim: int,
    embed_batch_size: int,
    task_type: str,
    retries: int,
    retry_min_seconds: float,
) -> BaseEmbedding:
    """Build a LlamaIndex-compatible embedding model backed by Google GenAI."""
    return GoogleGenAIEmbedding(
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
