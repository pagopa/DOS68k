from enum import StrEnum
from functools import lru_cache
from pydantic_settings import BaseSettings


class AgentProvider(StrEnum):
    LLAMAINDEX_GOOGLE = "llamaindex_google"
    LLAMAINDEX_OPENAI = "llamaindex_openai"


class AgentSettings(BaseSettings):
    AGENT_PROVIDER: AgentProvider


@lru_cache
def get_agent_settings() -> AgentSettings:
    return AgentSettings()
