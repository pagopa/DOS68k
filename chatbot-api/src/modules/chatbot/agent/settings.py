from functools import lru_cache
from typing import Optional, Tuple, Annotated
from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, YamlConfigSettingsSource, PydanticBaseSettingsSource

class AgentYamlSettings(BaseSettings):
    name: Annotated[Optional[str], Field(default=None)]
    description: Annotated[Optional[str], Field(default=None)]
    system_prompt: Annotated[Optional[str], Field(default=None)]
    system_header: Annotated[Optional[str], Field(default=None)]


@lru_cache
def get_agent_yaml_settings(file: Path) -> AgentYamlSettings:
    class _Settings(AgentYamlSettings):
        @classmethod
        def settings_customise_sources(
                cls,
                settings_cls,
                init_settings: PydanticBaseSettingsSource,
                env_settings: PydanticBaseSettingsSource,
                dotenv_settings: PydanticBaseSettingsSource,
                file_secret_settings: PydanticBaseSettingsSource,
            ) -> Tuple[YamlConfigSettingsSource]:
            return (YamlConfigSettingsSource(settings_cls=cls, yaml_file=file),)

    return _Settings()