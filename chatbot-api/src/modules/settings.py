from functools import lru_cache
from typing import Annotated, Literal
from pydantic import Field, PositiveInt, PositiveFloat
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Logging
    log_level: Annotated[int, Field(default=20)]  # logging.INFO = 20

    # Chatbot release tag (appended to every response in "products")
    chatbot_release: Annotated[str, Field(default="0.1.0")]

    # Redis vector index IDs (must match the IDs used during indexing)
    devportal_index_id: str
    cittadino_index_id: str

    # LlamaIndex chunking settings (must match the settings used during indexing)
    chunk_size: Annotated[PositiveInt, Field(default=512)]
    chunk_overlap: Annotated[PositiveInt, Field(default=50)]

    # Prompt templates (populated via environment variables or .env file)
    qa_prompt_str: str
    refine_prompt_str: str

    # LLM / Embedding provider ("google" | "mock")
    provider: Annotated[Literal["google", "mock"], Field(default="google")]
    google_api_key: Annotated[str, Field(default="")]

    # LLM settings
    model_id: str
    temperature_rag: Annotated[PositiveFloat, Field(default=0.1)]
    max_tokens: Annotated[PositiveInt, Field(default=1024)]

    # Embedding settings
    embed_model_id: str
    embed_dim: Annotated[PositiveInt, Field(default=768)]  # gemini text-embedding-004 default
    embed_batch_size: Annotated[PositiveInt, Field(default=100)]
    embed_task: Annotated[str, Field(default="RETRIEVAL_QUERY")]
    embed_retries: Annotated[PositiveInt, Field(default=3)]
    embed_retry_min_seconds: Annotated[PositiveFloat, Field(default=1.0)]

    # Retrieval settings
    similarity_topk: Annotated[PositiveInt, Field(default=5)]
    use_async: Annotated[bool, Field(default=True)]

    # Agent settings
    temperature_agent: Annotated[PositiveFloat, Field(default=0.0)]
    discovery_system_prompt_str: str
    react_system_str: str


@lru_cache
def get_settings() -> Settings:
    return Settings()


SETTINGS: Settings = get_settings()
