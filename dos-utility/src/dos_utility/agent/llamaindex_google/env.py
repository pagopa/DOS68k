from functools import lru_cache
from typing import Annotated
from pydantic import Field, PositiveInt, PositiveFloat, NonNegativeFloat, SecretStr
from pydantic_settings import BaseSettings


class LlamaIndexGoogleAgentSettings(BaseSettings):
    """Settings for the LlamaIndex + Google GenAI agent provider."""

    # LLM
    MODEL_ID: Annotated[
        str, Field(description="Google GenAI model identifier (e.g. gemini-2.5-flash).")
    ]
    MODEL_API_KEY: Annotated[
        SecretStr, Field(description="API key for the Google GenAI service.")
    ]
    MAX_TOKENS: Annotated[PositiveInt, Field(default=1024)]
    TEMPERATURE_AGENT: Annotated[
        NonNegativeFloat,
        Field(default=0.0, description="Sampling temperature (0.0 = deterministic)."),
    ]

    # Embedding
    EMBED_MODEL_ID: Annotated[
        str, Field(description="Google GenAI embedding model identifier.")
    ]
    EMBED_DIM: Annotated[
        PositiveInt,
        Field(
            default=768,
            description="Embedding output dimensionality (must match the index dim).",
        ),
    ]
    EMBED_BATCH_SIZE: Annotated[PositiveInt, Field(default=100)]
    EMBED_TASK: Annotated[
        str,
        Field(
            default="RETRIEVAL_QUERY",
            description="Embedding task type (RETRIEVAL_QUERY | RETRIEVAL_DOCUMENT | SEMANTIC_SIMILARITY).",
        ),
    ]
    EMBED_RETRIES: Annotated[PositiveInt, Field(default=3)]
    EMBED_RETRY_MIN_SECONDS: Annotated[PositiveFloat, Field(default=1.0)]

    # Retrieval
    SIMILARITY_TOPK: Annotated[
        PositiveInt,
        Field(
            default=5,
            description="Default number of top chunks to retrieve per RAG tool call.",
        ),
    ]


@lru_cache
def get_llamaindex_google_agent_settings() -> LlamaIndexGoogleAgentSettings:
    return LlamaIndexGoogleAgentSettings()
