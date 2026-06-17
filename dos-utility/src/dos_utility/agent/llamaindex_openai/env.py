from functools import lru_cache
from typing import Annotated, Optional
from pydantic import Field, NonNegativeFloat, PositiveInt, SecretStr
from pydantic_settings import BaseSettings


class LlamaIndexOpenAIAgentSettings(BaseSettings):
    """Settings for the LlamaIndex + OpenAI agent provider."""

    # LLM
    MODEL_ID: Annotated[
        str, Field(description="OpenAI chat model identifier (e.g. gpt-4o-mini).")
    ]
    MODEL_API_KEY: Annotated[
        SecretStr, Field(description="API key for the OpenAI service.")
    ]
    MAX_TOKENS: Annotated[PositiveInt, Field(default=1024)]
    TEMPERATURE_AGENT: Annotated[
        NonNegativeFloat,
        Field(default=0.0, description="Sampling temperature (0.0 = deterministic)."),
    ]
    OPENAI_API_BASE: Annotated[
        Optional[str],
        Field(
            default=None,
            description="Optional override for the OpenAI-compatible API base URL.",
        ),
    ]

    # Embedding
    EMBED_MODEL_ID: Annotated[
        str, Field(description="OpenAI embedding model identifier (e.g. text-embedding-3-small).")
    ]
    EMBED_DIM: Annotated[
        PositiveInt,
        Field(
            default=1536,
            description="Embedding output dimensionality (must match the index dim).",
        ),
    ]
    EMBED_BATCH_SIZE: Annotated[PositiveInt, Field(default=100)]
    EMBED_RETRIES: Annotated[PositiveInt, Field(default=3)]

    # Retrieval
    SIMILARITY_TOPK: Annotated[
        PositiveInt,
        Field(
            default=5,
            description="Default number of top chunks to retrieve per RAG tool call.",
        ),
    ]


@lru_cache
def get_llamaindex_openai_agent_settings() -> LlamaIndexOpenAIAgentSettings:
    return LlamaIndexOpenAIAgentSettings()
