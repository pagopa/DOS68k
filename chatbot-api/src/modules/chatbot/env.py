from functools import lru_cache
from pathlib import Path
from typing import Annotated, Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class ChatbotSettings(BaseSettings):
    # Tool config directory — mount a volume here to provide your own YAML tool configs.
    # Defaults to the chatbot module's built-in config/ folder.
    tools_config_dir: Annotated[
        Optional[Path], Field(default=Path(__file__).parent / "tool" / "config")
    ]

    # Path to a YAML agent config file (name, description, system_prompt, system_header).
    # Defaults to the built-in agent.yaml shipped with this module.
    agent_config_path: Annotated[
        Optional[Path], Field(default=Path(__file__).parent / "agent" / "agent.yaml")
    ]


@lru_cache
def get_chatbot_settings() -> ChatbotSettings:
    return ChatbotSettings()
