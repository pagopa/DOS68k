from functools import lru_cache
from pathlib import Path
from typing import Annotated, Optional, Literal
from pydantic import Field, PositiveInt, PositiveFloat, NonNegativeFloat
from pydantic_settings import BaseSettings


class ChatbotSettings(BaseSettings):
    # LLM / Embedding provider ("google", "mock")
    provider: Annotated[Literal["google", "mock"], Field(default="mock")]
    model_id: Annotated[Optional[str], Field(default=None, description="Do not set if provider is 'mock'")]
    model_api_key: Annotated[Optional[str], Field(default=None, description="API key for the chosen provider. Do not set if provider is 'mock'")]

    # LLM settings
    max_tokens: Annotated[PositiveInt, Field(default=1024)]

    # Embedding settings
    embed_model_id: Annotated[str, Field(default="mock")]
    embed_batch_size: Annotated[PositiveInt, Field(default=100)]
    embed_dim: Annotated[PositiveInt, Field(default=768)]
    embed_task: Annotated[str, Field(default="RETRIEVAL_QUERY")]
    embed_retries: Annotated[PositiveInt, Field(default=3)]
    embed_retry_min_seconds: Annotated[PositiveFloat, Field(default=1.0)]

    # Retrieval settings
    similarity_topk: Annotated[PositiveInt, Field(default=5)]

    # Tool config directory — mount a volume here to provide your own YAML tool configs.
    # Defaults to the chatbot module's built-in config/ folder.
    tools_config_dir: Annotated[Optional[Path], Field(default=None)]

    # Agent settings
    temperature_agent: Annotated[NonNegativeFloat, Field(default=0.0)]  # 0.0 = deterministic
    # Path to a YAML agent config file (name, description, system_prompt, system_header).
    # Defaults to the built-in agent.yaml shipped with this module.
    agent_config_path: Annotated[Optional[Path], Field(default=Path(__file__).parent / "agent" / "agent.yaml")]


@lru_cache
def get_chatbot_settings() -> ChatbotSettings:
    return ChatbotSettings()
