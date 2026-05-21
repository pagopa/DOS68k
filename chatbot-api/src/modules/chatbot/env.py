from functools import lru_cache
from pathlib import Path
from typing import Annotated, Optional, Literal, Self

from pydantic import Field, PositiveInt, PositiveFloat, NonNegativeFloat, model_validator
from pydantic_settings import BaseSettings
from dos_utility.types.models import Provider

class ChatbotSettings(BaseSettings):
    # LLM / Embedding provider
    provider: Provider

    # LLM settings
    max_tokens: Annotated[PositiveInt, Field(default=1024)]
    model_id: Annotated[
        str, Field(description="ID of the model for the chosen provider")
    ]
    model_api_key: Annotated[str | None, Field(default=None, description="API key for the chosen provider")]
    base_url: Annotated[str | None, Field(default=None, description="Base URL for the chosen provider")]
    request_timeout: Annotated[float | None, Field(default=None, description="Model response timeout")]

    # Embedding settings
    embed_provider: Provider
    embed_model_id: Annotated[
        str, Field(description="ID of the embedding model for the chosen provider")
    ]
    embed_batch_size: Annotated[PositiveInt, Field(default=100)]
    embed_dim: Annotated[PositiveInt, Field(default=768)]
    embed_task: Annotated[str, Field(default="RETRIEVAL_QUERY")]
    embed_retries: Annotated[PositiveInt, Field(default=3)]
    embed_retry_min_seconds: Annotated[PositiveFloat, Field(default=1.0)]
    embed_base_url: Annotated[str | None, Field(default=None, description="Base URL for the chosen embedding provider")]

    # Retrieval settings
    similarity_topk: Annotated[PositiveInt, Field(default=5)]

    # Tool config directory — mount a volume here to provide your own YAML tool configs.
    # Defaults to the chatbot module's built-in config/ folder.
    tools_config_dir: Annotated[
        Optional[Path], Field(default=Path(__file__).parent / "tool" / "config")
    ]

    # Agent settings
    temperature_agent: Annotated[
        NonNegativeFloat, Field(default=0.0)
    ]  # 0.0 = deterministic
    # Path to a YAML agent config file (name, description, system_prompt, system_header).
    # Defaults to the built-in agent.yaml shipped with this module.
    agent_config_path: Annotated[
        Optional[Path], Field(default=Path(__file__).parent / "agent" / "agent.yaml")
    ]

    @model_validator(mode="after")
    def validate_provider_specific_configs(self) -> Self:
        if self.provider == "google":
            if not self.model_api_key:
                raise ValueError(
                    "[Provider: Google] 'model_api_key' is mandatory. "
                    "Please set it in your .env file."
                )

        return self


@lru_cache
def get_chatbot_settings() -> ChatbotSettings:
    return ChatbotSettings()
